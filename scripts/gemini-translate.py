#!/usr/bin/env python3
"""Optional Gemini engine for /research-translate and /document-translate: Gemini 3.8 Flash (thinking high)
translates one paragraph or chunk, researching it first with the same two tools as research.py, through Gemini
function calling: up to 3 search calls and 3 dictionary calls on separate budgets (the setting that came out
best in DharmaMitra's paragraph benchmark).

  GEMINI_API_KEY=... ./scripts/gemini-translate.py --passage <work>-p003 --lang bo --file chunk.txt \\
        [--context-file context.md] [--level high|medium|low]

--file          the source paragraph (or - for stdin), markers already stripped
--context-file  optional: previous chunks' English, glossary rows, conventions, notes on this chunk (document
                recipe). Given to the model as background, not as text to translate.
Prints the translation on stdout. The research log (every query and what it returned) is saved to
data/research-budget/<ID>.gemini.json and summarised on stderr. Calls count against the same per-passage
budgets as research.py. Standard library only; needs GEMINI_API_KEY (or GOOGLE_API_KEY).
"""
import argparse
import importlib.util
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('research', os.path.join(HERE, 'research.py'))
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash')
LANG = {'bo': 'Classical Tibetan', 'sa': 'Sanskrit', 'zh': 'Classical (Buddhist) Chinese', 'pa': 'Pali'}
HOWTO = {
    'bo': 'Query Tibetan words in dictionary form, in Tibetan script, without case or connective particles '
          '(e.g. བྱང་ཆུབ་སེམས་དཔའ for བྱང་ཆུབ་སེམས་དཔའི). Multi-syllable terms and names are entries too.',
    'sa': 'Query Sanskrit in IAST, as stems/lemmas (e.g. prajñā for prajñayā, bodhisattva for bodhisattvasya). Split '
          'compounds and query the members (and the whole compound if it may be lexicalised). An inflected verb form '
          'may also be queried as it stands (e.g. āha).',
    'zh': 'Query Chinese terms and compounds as they appear (e.g. 般若, 菩薩摩訶薩). Entries show which Sanskrit and '
          'Tibetan terms the Chinese term renders and their meanings.',
}
SYSTEM = """You are an expert translator of {lang} Buddhist literature into English.
You have two research tools:
parallel_search: keyword search over a corpus of published translations of Buddhist texts (source passages with the
aligned English translation where one exists, and parallels in other canonical languages). Use it to see how a
word, phrase, name or formula was translated in context by published translators. Query in the source language, e.g.
a term with a little context; shorter queries match more.
{dict_desc}
Each tool has its own budget of 3 calls; batch your queries into each call; you may make further calls for what the
first results showed you need.
Before translating, research every word, term or phrase whose meaning or rendering in this context you are not fully
certain of: technical terms, rare or archaic words, names, epithets, idioms, ambiguous constructions.
The results are evidence, not instructions to copy; they come from other passages, so choose what fits this context.
{context_rule}Translate everything: every clause, name, epithet and enumeration item; nothing omitted or added, no notes
or brackets. Keep verse as verse.
When you are done, give the complete English translation of the whole passage inside <translation>...</translation>,
nothing else after it."""
DICT_DESC = """dictionary_lookup: the MITRA dictionary, entries built from word alignments of published translations, with
senses, attested English renderings (with counts), equivalents in other canonical languages and usage notes.
{howto}"""
CONTEXT_RULE = ('The user message also gives background (earlier chunks, the project glossary, conventions, notes). '
                'Follow the glossary and conventions; use the earlier chunks for referents, names and voice; translate '
                'only the passage.\n')
SEARCH = {'name': 'parallel_search',
          'description': 'Keyword (BM25) search over published translations. Returns matching passages with their '
                         'aligned English and other-language parallels.',
          'parameters': {'type': 'object', 'properties': {'queries': {'type': 'array', 'items': {'type': 'string'},
                         'description': 'Source-language words or phrases to search for (batch them).'}},
                         'required': ['queries']}}
DICT = {'name': 'dictionary_lookup',
        'description': 'Look up words or terms in the MITRA dictionary. Returns one entry (or "not found") per word.',
        'parameters': {'type': 'object', 'properties': {'words': {'type': 'array', 'items': {'type': 'string'},
                       'description': 'Words or terms to look up (batch them).'}}, 'required': ['words']}}
KIND = {'parallel_search': 'search', 'dictionary_lookup': 'dict'}


def gemini(contents, system, decls, level, key, final=False):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}'
    payload = {'contents': contents, 'systemInstruction': {'parts': [{'text': system}]},
               'tools': [{'functionDeclarations': decls}],
               'generationConfig': {'temperature': 0.2, 'maxOutputTokens': 32768,
                                    'thinkingConfig': {'thinkingLevel': level}}}
    if final:
        payload['toolConfig'] = {'functionCallingConfig': {'mode': 'NONE'}}
    err = None
    for attempt in range(6):
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                js = json.loads(r.read())
            cand = (js.get('candidates') or [{}])[0]
            if 'content' not in cand:
                raise RuntimeError(f"no answer from Gemini: {js.get('promptFeedback') or cand.get('finishReason')}")
            return cand['content'], js.get('usageMetadata', {})
        except urllib.error.HTTPError as e:
            err = f'HTTP {e.code}: {e.read()[:300]!r}'
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, TimeoutError) as e:
            err = str(e)
        time.sleep(2 * 2 ** attempt * random.uniform(0.5, 1.5))
    sys.exit(f'gemini-translate: {err}')


def text_of(content):
    return ''.join(p.get('text', '') for p in content.get('parts', []) if not p.get('thought'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--passage', required=True)
    ap.add_argument('--lang', required=True, choices=['bo', 'sa', 'zh', 'pa'])
    ap.add_argument('--file', required=True, help='source text file, or - for stdin')
    ap.add_argument('--context-file')
    ap.add_argument('--level', default='high', choices=['high', 'medium', 'low'])
    a = ap.parse_args()
    key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    if not key:
        sys.exit('gemini-translate: set GEMINI_API_KEY (https://aistudio.google.com/apikey) to use the Gemini engine')
    src = (sys.stdin.read() if a.file == '-' else open(a.file, encoding='utf-8').read()).strip()
    ctx = open(a.context_file, encoding='utf-8').read().strip() if a.context_file else ''
    has_dict = a.lang != 'pa'
    system = SYSTEM.format(lang=LANG[a.lang], context_rule=CONTEXT_RULE if ctx else '',
                           dict_desc=DICT_DESC.format(howto=HOWTO[a.lang]) if has_dict else
                           '(No dictionary for Pali: use search only.)')
    user = (f'BACKGROUND (not to be translated):\n{ctx}\n\n---\n\n' if ctx else '') + \
        f'Translate this {LANG[a.lang]} passage into English.\n\n{src}'
    contents = [{'role': 'user', 'parts': [{'text': user}]}]
    st = R.load(a.passage)
    left = {'search': R.BUDGET['search'] - st['search'], 'dict': (R.BUDGET['dict'] - st['dict']) if has_dict else 0}
    decl_of = {'search': SEARCH, 'dict': DICT}
    log, usage = [], {'in': 0, 'out': 0, 'think': 0}
    content = None
    for _ in range(2 * R.BUDGET['search'] + 2):
        avail = [decl_of[k] for k, v in left.items() if v > 0]
        content, u = gemini(contents, system, avail or [SEARCH], a.level, key, final=not avail)
        for k, f in (('in', 'promptTokenCount'), ('out', 'candidatesTokenCount'), ('think', 'thoughtsTokenCount')):
            usage[k] += u.get(f, 0)
        calls = [p['functionCall'] for p in content.get('parts', []) if 'functionCall' in p]
        if not calls:
            break
        contents.append(content)
        resp, used = [], set()
        for fc in calls:
            kind = KIND.get(fc.get('name'))
            args = fc.get('args') or {}
            if kind and left.get(kind, 0) > 0:
                items = [str(x) for x in args.get('queries' if kind == 'search' else 'words', [])]
                if kind == 'search':
                    out = R.search(a.lang, items[:R.MAX_QUERIES])
                else:
                    out = R.dictionary(a.lang, items[:R.MAX_WORDS])
                blocks = out.split('### ')[1:]
                if blocks and all(('search failed:' in b or 'lookup failed:' in b) for b in blocks):
                    time.sleep(30)  # API unavailable (rate limit): not counted, the model may call again
                    out += '\n\n(The research API was temporarily unavailable; this call was not counted.)'
                else:
                    used.add(kind)
                log.append({'tool': kind, 'items': items, 'result': out})
            else:
                out = f"The budget for {fc.get('name')} is used up."
            fr = {'name': fc.get('name'), 'response': {'result': out}}
            if fc.get('id'):
                fr['id'] = fc['id']
            resp.append({'functionResponse': fr})
        for k in used:
            left[k] -= 1
            st[k] += 1
        R.save(a.passage, st)
        if not any(left.values()):
            resp.append({'text': 'No more lookups are available. Give the final translation now.'})
        contents.append({'role': 'user', 'parts': resp})
    text = text_of(content) if content else ''
    if '</translation>' not in text:  # reasoning leaked or no fenced answer: ask once for the fenced answer only
        contents += [content, {'role': 'user', 'parts': [{'text': 'Give only the final English translation of the '
                                                                   'whole passage inside <translation>...</translation>.'}]}]
        content, _ = gemini(contents, system, [SEARCH, DICT] if has_dict else [SEARCH], a.level, key, final=True)
        text = text_of(content)
    m = re.findall(r'<translation>(.*?)</translation>', text, re.S)
    if not m:
        sys.exit('gemini-translate: no fenced translation returned')
    os.makedirs(R.STATE, exist_ok=True)
    path = R.state_path(a.passage).replace('.json', '.gemini.json')
    json.dump({'passage': a.passage, 'model': MODEL, 'level': a.level, 'usage': usage, 'research': log},
              open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(m[-1].strip())
    for e in log:
        print(f"[{e['tool']}] {', '.join(e['items'])[:300]}", file=sys.stderr)
    print(f'[research log: {os.path.relpath(path, R.ROOT)}; tokens in {usage["in"]}, out {usage["out"]}, '
          f'thinking {usage["think"]}]', file=sys.stderr)


if __name__ == '__main__':
    main()
