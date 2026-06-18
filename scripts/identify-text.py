#!/usr/bin/env python3
"""identify-text.py — resolve a human description to a DharmaNexus corpus filename, offline.

Reads the cached corpus index (data/corpus-index.json, built by build-corpus-index.py) and ranks
candidate texts for a fuzzy query like "yasomitra abhidharma commentary" or "perfection of wisdom
25000". Diacritics-insensitive. No network call (it auto-builds the index once if it's missing).

The winning `filename` is what you feed to `nexus.sh table <filename>` for an intertextuality run;
its segmentnrs (from /primary/ or table) go to `nexus.sh matches`.

Usage:
    scripts/identify-text.py "yasomitra abhidharma commentary"
    scripts/identify-text.py "vinayasutra gunaprabha" --lang sa
    scripts/identify-text.py "madhyamakavatara" --top 3
    scripts/identify-text.py "abhidharmakosa" --table     # human-readable instead of JSON

Output (default JSON): a ranked list of
    {lang, filename, displayName, collection, category, hits, ntoks, ratio, score}
where `hits` = query tokens found in the text's metadata blob, `ratio` = difflib similarity of the
whole query to the displayName, `score` = combined rank key. Higher is better.
"""
from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "corpus-index.json"
BUILD_SCRIPT = ROOT / "scripts" / "build-corpus-index.py"
STALE_DAYS = 45


def fold(s: str) -> str:
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def load_index() -> dict:
    if not INDEX_PATH.exists():
        print("identify-text: index missing, building it once "
              "(scripts/build-corpus-index.py)…", file=sys.stderr)
        subprocess.run([sys.executable, str(BUILD_SCRIPT), "--quiet"], check=False)
    if not INDEX_PATH.exists():
        sys.exit("identify-text: ERROR: could not build the corpus index "
                 "(network down?). Run scripts/setup.sh when online.")
    index = json.loads(INDEX_PATH.read_text())
    # staleness nudge — non-fatal; refresh is handled by the SessionStart hook / setup.sh
    import time
    age = (time.time() - float(index.get("fetched_at_epoch", 0))) / 86400.0
    if age > STALE_DAYS:
        print(f"identify-text: note: corpus index is {age:.0f} days old "
              f"(built {index.get('fetched_at','?')}); consider scripts/setup.sh --force",
              file=sys.stderr)
    return index


def score_entries(query: str, entries: list[dict], lang: str | None) -> list[dict]:
    qfold = fold(query)
    toks = [t for t in qfold.split() if t]
    results = []
    for e in entries:
        if lang and e["lang"] != lang:
            continue
        blob = e["blob"]
        hits = sum(1 for t in toks if t in blob)
        if hits == 0:
            continue
        ratio = difflib.SequenceMatcher(None, qfold, fold(e["displayName"])).ratio()
        # rank by token coverage first, then by name similarity
        score = hits + ratio
        results.append({
            "lang": e["lang"],
            "filename": e["filename"],
            "displayName": e["displayName"],
            "collection": e["collection"],
            "category": e["category"],
            "hits": hits,
            "ntoks": len(toks),
            "ratio": round(ratio, 3),
            "score": round(score, 3),
        })
    results.sort(key=lambda r: (-r["hits"], -r["ratio"], r["filename"]))
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Fuzzy-resolve a text description to a corpus filename.")
    ap.add_argument("query", nargs="+", help="description / title / author tokens")
    ap.add_argument("--lang", choices=["sa", "bo", "zh", "pa"], help="restrict to one language")
    ap.add_argument("--top", type=int, default=10, help="number of candidates (default 10)")
    ap.add_argument("--table", action="store_true", help="human-readable table instead of JSON")
    args = ap.parse_args()

    query = " ".join(args.query)
    index = load_index()
    results = score_entries(query, index["entries"], args.lang)[: args.top]

    if not results:
        print(f"identify-text: no candidates for {query!r}"
              + (f" in lang={args.lang}" if args.lang else ""), file=sys.stderr)
        print("[]" if not args.table else "(no matches)")
        return 0

    if args.table:
        w = max(len(r["filename"]) for r in results)
        for r in results:
            print(f"{r['hits']}/{r['ntoks']}  {r['ratio']:.2f}  {r['lang']}  "
                  f"{r['filename']:<{w}}  {r['displayName']}  [{r['collection']} / {r['category']}]")
    else:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
