#!/usr/bin/env python3
"""Research tools for the /research-translate recipe: parallel-passage search and MITRA dictionary lookup,
each with its own per-passage budget of 3 calls (the "3 + 3" setting).

  ./scripts/research.py search --passage ID --lang bo QUERY [QUERY ...]   (<= 20 queries per call)
  ./scripts/research.py dict   --passage ID --lang bo WORD [WORD ...]     (<= 40 words per call)
  ./scripts/research.py budget --passage ID                               (calls left)

search: BM25 over the canonical corpus (POST /api-search/primary/, search_type=regular, no reranking), then the
        DharmaNexus parallels of every hit (POST /api-db/matches/): the published English translation of the
        passage where one is aligned (84000, Tsadra, ...) and parallels in the other canon languages.
dict:   MITRA dictionary entries (dictionary.dharmamitra.org /api/summary): senses, attested renderings with
        counts, usage notes. Tibetan (Unicode or Wylie) and Sanskrit (IAST) headwords; Chinese terms are answered
        with their attested Tibetan and Sanskrit equivalents and the meaning of the main one.
One call = one batch. A call beyond the budget prints a notice and does nothing. Budgets live in
data/research-budget/<ID>.json, and every call's full result is also saved there (<ID>.search1.md, ...),
so output cut off on screen can be reread without spending another call. Standard library only.
"""
import argparse
import http.client
import json
import os
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

PRIMARY = 'https://dharmamitra.org/api-search/primary/'
MATCHES = 'https://dharmamitra.org/api-db/matches/'
DICT = 'https://dictionary.dharmamitra.org/api/'
UA = 'dharmamitra-claude-code-agent/1.0 (research.py)'
BUDGET = {'search': 3, 'dict': 3}
MAX_QUERIES, MAX_WORDS, HITS_PER_QUERY, ENTRY_CHARS = 20, 40, 3, 1800
SEARCH_WORKERS, DICT_WORKERS = 3, 3  # concurrent requests; stays within the per-client limits with backoff
LANG_NAME = {'EN': 'English', 'ZH': 'Chinese', 'SA': 'Sanskrit', 'BO': 'Tibetan', 'PA': 'Pali'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, 'data', 'research-budget')


_tls = threading.local()


class ApiError(Exception):
    pass


def _conn(host):
    """One keep-alive HTTPS connection per host and thread (a fresh TLS handshake through Cloudflare can take seconds)."""
    pool = getattr(_tls, 'pool', None)
    if pool is None:
        pool = _tls.pool = {}
    if host not in pool:
        pool[host] = http.client.HTTPSConnection(host, timeout=90)
    return pool[host]


def http_json(url, body=None, min_gap=0.0):
    """GET (body None) or POST JSON over a kept-alive connection, with backoff on 429/5xx and reconnect on errors."""
    u = urllib.parse.urlsplit(url)
    path = u.path + ('?' + u.query if u.query else '')
    headers = {'User-Agent': UA, 'Content-Type': 'application/json', 'Connection': 'keep-alive'}
    for attempt in range(6):
        conn = _conn(u.netloc)
        try:
            conn.request('POST' if body is not None else 'GET', path,
                         body=json.dumps(body).encode() if body is not None else None, headers=headers)
            r = conn.getresponse()
            data = r.read()
            if r.status in (429, 500, 502, 503, 504, 524) and attempt < 5:
                time.sleep(_backoff(attempt, r.getheader('Retry-After')))
                continue
            if r.status >= 400:
                raise ApiError(f'HTTP {r.status} {r.reason}')
            return json.loads(data)
        except (http.client.HTTPException, OSError):
            conn.close()
            getattr(_tls, 'pool', {}).pop(u.netloc, None)
            if attempt < 5:
                time.sleep(_backoff(attempt))
                continue
            raise


def _backoff(attempt, retry_after=None):
    """Wait before retry `attempt`: the server's Retry-After if it sent one, else 2, 4, 8, 16, 32 s, each with
    random jitter so parallel threads and parallel users do not retry in lockstep."""
    try:
        if retry_after:
            return float(retry_after) + random.uniform(0, 1)
    except ValueError:
        pass
    return 2 * 2 ** attempt * random.uniform(0.5, 1.5)


def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()


# ---------- search ----------

def _norm(x):
    return re.sub(r'[\s\W_]+', '', unicodedata.normalize('NFC', x or '').lower())


def _exclusion():
    """Evaluation only: RESEARCH_EXCLUDE=<json file with "src" and "ref"> drops hits that contain (or are contained in)
    the passage being translated, and English parallels equal to a line of its reference translation."""
    p = os.environ.get('RESEARCH_EXCLUDE')
    if not p:
        return None
    d = json.load(open(p, encoding='utf-8'))
    lines = [x for x in re.split(r'\n|(?<=[/。])', d.get('src', '')) if len(_norm(x)) >= 4]
    return {'src': _norm(d.get('src')), 'sent': [_norm(x) for x in lines],
            'ref': {_norm(x) for x in (d.get('ref') or '').split('\n') if len(_norm(x)) > 10}}


def _excluded(ex, text):
    a = _norm(text)
    return bool(ex) and ((len(a) > 10 and a in ex['src']) or any(len(x) > 10 and x in a for x in ex['sent']))

def search(lang, queries):
    ex = _exclusion()
    def one(q):
        body = {'search_input': q, 'search_type': 'regular', 'do_ranking': False, 'filter_source_language': lang,
                'include_vectors': False, 'max_results': HITS_PER_QUERY + 2}
        try:
            res = http_json(PRIMARY, body).get('results', [])
        except Exception as e:  # noqa: BLE001
            return (q, None, f'search failed: {e}')
        seen, hits = set(), []
        for h in res:
            t = clean(h.get('text'))
            if not t or t in seen or _excluded(ex, t):
                continue
            seen.add(t)
            segs = h.get('all_segmentnrs') or [h.get('segmentnr')]
            if isinstance(segs, str):
                segs = re.findall(r"[A-Z]{2}_[^',\]\s]+", segs)
            hits.append({'text': t, 'title': clean(h.get('title')), 'segs': [s for s in segs if s][:8],
                         'link': h.get('src_link', '')})
            if len(hits) >= HITS_PER_QUERY:
                break
        return (q, hits, None)

    with ThreadPoolExecutor(SEARCH_WORKERS) as pool:  # the API allows 3 requests/s per client
        hits_by_q = list(pool.map(one, queries))
    # one /matches/ call for all hits of this batch
    segs = sorted({s for _, hits, _ in hits_by_q if hits for h in hits for s in h['segs']})[:120]
    matches = []
    if segs:
        try:
            matches = http_json(MATCHES, {'segment_nrs': segs}).get('matches', [])
        except Exception:  # noqa: BLE001
            matches = []
    out = []
    for q, hits, err in hits_by_q:
        out.append(f'### {q}')
        if err:
            out.append(err)
            continue
        if not hits:
            out.append('no hits')
            continue
        for h in hits:
            mine = [m for m in matches if set(m.get('root_segnr') or []) & set(h['segs'])]
            par, en = {}, []
            for m in sorted(mine, key=lambda m: -(m.get('score') or 0)):
                code = (m.get('par_segnr') or ['??'])[0][:2]
                pt = clean(m.get('par_text'))
                if code == lang.upper() or not pt or (ex and _norm(pt) in ex['ref']):
                    continue
                name = clean((m.get('par_full_names') or {}).get('display_name'))[:60]
                if code == 'EN':
                    if len(en) < 2 and all(pt != e[1] for e in en):
                        en.append((clean(m.get('root_text'))[:120], pt[:350], name))
                elif code not in par:
                    par[code] = f'{LANG_NAME.get(code, code)} ({name}): {pt[:300]}'
            lines = [f'- {h["text"][:350]}', f'  [{h["title"][:80]}] {h["link"]}']
            lines += [f'  = English ({n}) for the source line "{r}…": {t}' for r, t, n in en]
            lines += [f'  = {par[c]}' for c in ('SA', 'ZH', 'BO', 'PA') if c in par]
            out.append('\n'.join(lines))
    return '\n\n'.join(out)


# ---------- dictionary ----------

BO_PARTICLES = ('ཀྱི', 'གྱི', 'གི', 'ཡི', 'ཀྱིས', 'གྱིས', 'གིས', 'ཡིས', 'ལ', 'ན', 'དུ', 'ཏུ', 'སུ', 'རུ', 'ལས', 'ནས',
                'དང', 'ནི', 'ཏེ', 'སྟེ', 'དེ', 'ཅིང', 'ཞིང', 'ཤིང', 'ཀྱང', 'ཡང', 'འང', 'ཅེས', 'ཞེས', 'ཤེས')
NOMINALISERS = ('པ', 'བ', 'པོ', 'བོ')
SA_ENDINGS = [('asya', 'a'), ('ānām', 'a'), ('ebhyaḥ', 'a'), ('eṣu', 'a'), ('aiḥ', 'a'), ('ena', 'a'), ('āya', 'a'),
              ('āt', 'a'), ('āni', 'a'), ('āḥ', 'a'), ('aḥ', 'a'), ('am', 'a'), ('aṃ', 'a'), ('e', 'a'), ('āyāḥ', 'ā'),
              ('āyām', 'ā'), ('ayā', 'ā'), ('ām', 'ā'), ('āṃ', 'ā'), ('ayaḥ', 'i'), ('ibhiḥ', 'i'), ('eḥ', 'i'),
              ('iḥ', 'i'), ('im', 'i'), ('oḥ', 'u'), ('uḥ', 'u'), ('um', 'u'), ('ā', 'a'), ('ī', 'in'), ('inaḥ', 'in'),
              ('ā', 'an'), ('ānam', 'an'), ('tā', 'tṛ'), ('vān', 'vat'), ('mān', 'mat'), ('ḥ', ''), ('ṃ', ''), ('m', '')]


def bo_candidates(w):
    w = w.strip().strip('་།༎ /')
    syl = [s for s in re.split('[་]+', w) if s]
    cands = [w]
    if syl and syl[-1] in BO_PARTICLES and len(syl) > 1:
        cands.append('་'.join(syl[:-1]))
    for c in list(cands):
        s = c.split('་')
        last = s[-1]
        for suf in ('འི', 'འོ', 'ས', 'ར'):  # genitive/terminating/agentive/terminative fused to the last syllable
            if last.endswith(suf) and len(last) > len(suf):
                base = last[:-len(suf)]
                if suf in ('འི', 'འོ'):  # dpa'i -> dpa', lha'i -> lha
                    cands.append('་'.join(s[:-1] + [base + 'འ']))
                cands.append('་'.join(s[:-1] + [base]))
                if suf in ('ས', 'ར'):
                    cands.append('་'.join(s[:-1] + [base + 'འ']))
    for c in list(cands):
        s = c.split('་')
        cands.append('་'.join(s[:-1]) if s[-1] in NOMINALISERS and len(s) > 1 else c + '་པ')
    if len(syl) >= 3:  # sub-phrases of a long term: without its first syllable(s), without its last one
        cands += ['་'.join(syl[1:]), '་'.join(syl[2:]), '་'.join(syl[:-1])]
    out = []
    for c in cands:
        if c and c not in out:
            out.append(c)
    return out[:8]


def sa_candidates(w):
    w = w.strip().strip('/|.,;:!?()-–—\'"“”').replace('-', '')
    cands = [w]
    for e, r in SA_ENDINGS:
        if w.endswith(e) and len(w) > len(e) + 1:
            cands.append(w[:-len(e)] + r)
    out = []
    for c in cands:
        if c and c not in out:
            out.append(c)
    return out[:6]


def render_entry(js):
    head = js.get('head') or js.get('term')
    lines = [f"{js.get('head_unicode') or head}" + (f' ({head})' if js.get('head_unicode') and head else '')]
    for i, s in enumerate((js.get('senses') or [])[:6], 1):
        t = f'{i}. {clean(s.get("definition"))}'
        if s.get('note'):
            t += f' Note: {clean(s["note"])}'
        rend = []
        for lg in ('en', 'sa', 'bo', 'zh'):
            xs = (s.get('rend') or {}).get(lg) or []
            if xs:
                rend.append(f"{LANG_NAME[lg.upper()]}: " + ', '.join(f"{x.get('u') or x['g']} ({x['n']})" for x in xs[:5]))
        if rend:
            t += ' [' + '; '.join(rend) + ']'
        lines.append(t)
    if js.get('usage'):
        lines.append('Usage: ' + clean(js['usage']))
    return '\n'.join(lines)[:ENTRY_CHARS]


def summary(term, lang):
    js = http_json(DICT + 'summary?' + urllib.parse.urlencode({'term': term, 'lang': lang}))
    return js if js.get('found') else None


def look_zh(w):
    w = re.sub(r'[\s，。、；：「」『』？！]', '', w)
    parts = []
    for par in ('bo', 'sa'):
        try:
            e = http_json(DICT + 'entry?' + urllib.parse.urlencode({'term': w, 'lang': 'zh', 'par': par}))
        except Exception:  # noqa: BLE001
            continue
        rel = sorted(e.get('related') or [], key=lambda r: -r.get('count', 0))[:4]
        if rel:
            parts.append((par, rel))
    if not parts:
        return None
    lines = [f'{w}: attested as the Chinese rendering of']
    for par, rel in parts:
        lines.append(f"- {LANG_NAME[par.upper()]}: " + ', '.join(
            f"{r['word']}{' (' + r['wylie'] + ')' if r.get('wylie') else ''} ({r.get('count', 0)}x)" for r in rel))
    par, rel = parts[0]
    top = summary(rel[0]['word'], par)
    if top and top.get('senses'):
        lines.append(f"Main equivalent {rel[0]['word']}: {clean(top['senses'][0].get('definition'))}")
    return '\n'.join(lines)[:ENTRY_CHARS]


def look(word, lang):
    if lang == 'zh':
        return look_zh(word)
    cands = bo_candidates(word) if lang == 'bo' else sa_candidates(word) if lang == 'sa' else [word]
    with ThreadPoolExecutor(len(cands)) as ex:  # all spelling variants at once, first found in order wins
        found = list(ex.map(lambda c: summary(c, lang), cands))
    for c, js in zip(cands, found):
        if js:
            txt = render_entry(js)
            return txt if c == cands[0] else f'(nearest entry: {c})\n{txt}'
    return None


def dictionary(lang, words):
    def one(w):
        try:
            return look(w, lang)
        except Exception as e:  # noqa: BLE001
            return f'lookup failed: {e}'
    with ThreadPoolExecutor(DICT_WORKERS) as ex:
        res = list(ex.map(one, words))
    return '\n\n'.join(f'### {w}\n{t or "not found (try the dictionary form, without particles or case endings)"}'
                         for w, t in zip(words, res))


# ---------- budget ----------

def state_path(pid):
    return os.path.join(STATE, re.sub(r'[^A-Za-z0-9._-]+', '_', pid) + '.json')


def load(pid):
    p = state_path(pid)
    return json.load(open(p)) if os.path.exists(p) else {'search': 0, 'dict': 0}


def save(pid, st):
    os.makedirs(STATE, exist_ok=True)
    json.dump(st, open(state_path(pid), 'w'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tool', choices=['search', 'dict', 'budget'])
    ap.add_argument('--passage', required=True, help='passage id, e.g. vajracchedika-p007')
    ap.add_argument('--lang', choices=['bo', 'sa', 'zh', 'pa'], help='source language')
    ap.add_argument('items', nargs='*', help='queries (search) or words (dict)')
    a = ap.parse_args()
    st = load(a.passage)
    if a.tool == 'budget':
        print(f"search calls left: {BUDGET['search'] - st['search']}, dictionary calls left: {BUDGET['dict'] - st['dict']}")
        return
    if not a.lang or not a.items:
        sys.exit('--lang and at least one query/word are required')
    if a.tool == 'dict' and a.lang == 'pa':
        sys.exit('the MITRA dictionary has no Pali entries; use search for Pali')
    if st[a.tool] >= BUDGET[a.tool]:
        print(f'The {a.tool} budget for this passage ({BUDGET[a.tool]} calls) is used up. '
              'Use what you have and write the translation.')
        return
    st[a.tool] += 1
    save(a.passage, st)
    text = search(a.lang, a.items[:MAX_QUERIES]) if a.tool == 'search' else dictionary(a.lang, a.items[:MAX_WORDS])
    blocks = [b for b in text.split('### ')[1:]]
    if blocks and all(('search failed:' in b or 'lookup failed:' in b) for b in blocks):
        st[a.tool] -= 1  # the API was unavailable (e.g. rate-limited): this call does not count
        save(a.passage, st)
        print(text)
        print(f"\n[every request in this call failed, so it was not counted; wait a minute and retry. "
              f"{BUDGET['search'] - st['search']} search and {BUDGET['dict'] - st['dict']} dictionary calls left]")
        return
    cache = os.path.join(STATE, re.sub(r'[^A-Za-z0-9._-]+', '_', a.passage) + f'.{a.tool}{st[a.tool]}.md')
    open(cache, 'w', encoding='utf-8').write(text + '\n')
    print(text)
    print(f"\n[full result saved to {os.path.relpath(cache, ROOT)}]")
    print(f"[{a.tool} call {st[a.tool]} of {BUDGET[a.tool]} for passage {a.passage}; "
          f"{BUDGET['search'] - st['search']} search and {BUDGET['dict'] - st['dict']} dictionary calls left]")


if __name__ == '__main__':
    main()
