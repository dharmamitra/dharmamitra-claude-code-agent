#!/usr/bin/env python3
"""build-corpus-index.py — cache the DharmaNexus corpus map locally for fast, offline text ID.

Downloads /api-db/menudata/ for every canon language, flattens it to one compact JSON index
(data/corpus-index.json), and stamps it with a fetch time. identify-text.py reads this index and
fuzzy-matches a human description ("Yaśomitra's Abhidharma commentary") to a corpus filename
without hitting the network.

The index is a cache, not source data: it is .gitignored and rebuilt on demand.

Usage:
    scripts/build-corpus-index.py                 # always rebuild
    scripts/build-corpus-index.py --if-missing    # build only if the index file is absent
    scripts/build-corpus-index.py --max-age-days 30   # rebuild if missing OR older than 30 days
    scripts/build-corpus-index.py --force         # rebuild unconditionally (alias for no flag)
    scripts/build-corpus-index.py --quiet         # only print on error / actual rebuild

Env:
    DHARMAMITRA_DB_URL   override API base (default https://dharmamitra.org/api-db)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

LANGUAGES = ["sa", "bo", "zh", "pa"]
BASE = os.environ.get("DHARMAMITRA_DB_URL", "https://dharmamitra.org/api-db").rstrip("/")
ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "data" / "corpus-index.json"


def fold(s: str) -> str:
    """Lowercase + strip diacritics, so 'Yaśomitra' and 'yasomitra' compare equal."""
    if not s:
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()


def fetch_menudata(lang: str) -> dict:
    url = f"{BASE}/menudata/?language={lang}"
    req = urllib.request.Request(url, headers={"accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_entries(quiet: bool) -> list[dict]:
    entries: list[dict] = []
    for lang in LANGUAGES:
        try:
            data = fetch_menudata(lang)
        except Exception as e:  # network / parse — skip the language but keep going
            print(f"build-corpus-index: WARNING: {lang} failed: {e}", file=sys.stderr)
            continue
        n0 = len(entries)
        for col in data.get("menudata", []):
            col_name = col.get("collectiondisplayname", col.get("collection", ""))
            for cat in col.get("categories", []):
                cat_name = cat.get("categorydisplayname", cat.get("category", ""))
                for f in cat.get("files", []):
                    blob = " ".join(
                        x for x in (
                            f.get("displayName", ""),
                            f.get("search_field", ""),
                            f.get("raw_metadata", ""),
                        ) if x
                    )
                    entries.append({
                        "lang": lang,
                        "filename": f.get("filename", ""),
                        "displayName": f.get("displayName", ""),
                        "collection": col_name,
                        "category": cat_name,
                        "blob": fold(blob),
                    })
        if not quiet:
            print(f"build-corpus-index: {lang}: {len(entries) - n0} files", file=sys.stderr)
    return entries


def should_rebuild(args) -> bool:
    if args.force or (not args.if_missing and args.max_age_days is None):
        return True
    if not INDEX_PATH.exists():
        return True
    if args.if_missing:
        return False  # exists, and that's all --if-missing cares about
    # --max-age-days
    try:
        meta = json.loads(INDEX_PATH.read_text())
        age_days = (time.time() - float(meta.get("fetched_at_epoch", 0))) / 86400.0
    except Exception:
        return True
    return age_days > args.max_age_days


def main() -> int:
    ap = argparse.ArgumentParser(description="Cache the DharmaNexus corpus map locally.")
    ap.add_argument("--if-missing", action="store_true", help="build only if the index is absent")
    ap.add_argument("--max-age-days", type=float, default=None,
                    help="rebuild if missing or older than N days")
    ap.add_argument("--force", action="store_true", help="rebuild unconditionally")
    ap.add_argument("--quiet", action="store_true", help="suppress per-language progress")
    args = ap.parse_args()

    if not should_rebuild(args):
        if not args.quiet:
            print(f"build-corpus-index: up to date ({INDEX_PATH})", file=sys.stderr)
        return 0

    entries = build_entries(args.quiet)
    if not entries:
        print("build-corpus-index: ERROR: fetched 0 entries; leaving any existing index in place",
              file=sys.stderr)
        return 1

    now = time.time()
    index = {
        "source": BASE,
        "languages": LANGUAGES,
        "fetched_at_epoch": now,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
        "count": len(entries),
        "entries": entries,
    }
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = INDEX_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(index, ensure_ascii=False))
    tmp.replace(INDEX_PATH)  # atomic
    print(f"build-corpus-index: wrote {len(entries)} entries to {INDEX_PATH} "
          f"({index['fetched_at']})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
