#!/usr/bin/env python3
"""
build_corpus.py — nyarlathotep (cosmic-horror register oracle) corpus builder.

Conceit: train the COSMIC-HORROR REGISTER, not the man. The voice is the
outer-god dread — the indifferent cosmos, forbidden knowledge, the unnameable,
sanity-eroding revelation — NOT a reconstruction of H. P. Lovecraft the person.
This structurally sidesteps HPL's documented racism: we channel the atmosphere,
not the bigotry. Public-domain source = cleanest release of the fleet.

Two-layer racism guard:
  1. TITLE BLOCKLIST — stories whose premise IS the racism are dropped whole.
  2. SLUR/TERM FILTER — every surviving chunk is scanned; any with a slur or
     HPL's racial-fear vocabulary is dropped (belt-and-suspenders).

Also drops non-fiction (essays/letters/bio/apparatus) — that's HPL-as-man;
we want the fiction's cosmic-horror prose.

Completion format ({"text": ...}), same rail as eschaton/muntzergeist.

Usage:
  python scripts/build_corpus.py            # write nyarlathotep-v1-completion.jsonl
  python scripts/build_corpus.py --dry-run  # stats only
"""
import argparse, hashlib, json, re, statistics
from pathlib import Path

SRC = Path("/Users/rayweiss/Desktop/Dev Work/bookfinder-library/"
           "the-collected-works-of-hp-lovecraft-stories-poems-and-essays-lovecraft-5d7d4cce/content.md")
OUT_DIR = Path("/Users/rayweiss/Desktop/Dev Work/nyarlathotep/corpus")

CHUNK_MIN_WORDS = 30
CHUNK_MAX_WORDS = 300

# Apparatus / HPL-as-man sections to skip (not cosmic-horror fiction prose).
SKIP_TITLES = {
    "h. p lovecraft", "cthulu mythos", "cthulhu mythos", "collected works",
    "introduction", "table of contents", "notes on writing weird fiction",
    "h. p. lovecraft", "history of the necronomicon", "chronology", "[notes]",
    "ibid", "supernatural horror in literature", "notes",
}
# Stories whose PREMISE is the racism — dropped whole. Matched after stripping
# any " - with <collaborator>" suffix and smart-quote normalization.
BLOCK_TITLES = {
    "the horror at red hook", "medusa's coil", "the street", "he",
    "facts concerning the late arthur jermyn and his family", "arthur jermyn",
    "on the creation of niggers", "polaris", "the temple", "the last test",
    "winged death", "the mound", "out of the aeons",
}

def block_key(title):
    """Normalize a title for blocklist matching: lowercase, straight quotes,
    strip ' - with <collaborator>' / ' — with ...' collaboration suffixes."""
    t = title.lower().replace("’", "'").replace("—", "-").strip()
    t = re.sub(r"\s*-\s*with\s+.*$", "", t).strip()
    return t
# Slur / racial-fear terms — any chunk containing one is dropped.
SLUR = re.compile(
    r"\b(nigger|niggers|negro|negroes|negress|mulatto|mongrel|swarthy\s+\w*foreign|"
    r"half-?caste|half-?breed|the\s+yellow\s+peril|chinaman|chinamen|squaw|"
    r"darky|darkies|coon|wop|dago|kike|gook)\b", re.I)

DEDUP = set()

def norm(s): return re.sub(r"\s+", " ", s).strip()
def hkey(t): return hashlib.sha1(re.sub(r"\W+", "", t.lower())[:200].encode()).hexdigest()

def split_long(p):
    words = p.split()
    if len(words) <= CHUNK_MAX_WORDS:
        return [p]
    sents = re.split(r"(?<=[.!?])\s+", p)
    out, cur = [], []
    for s in sents:
        cur.append(s)
        if len(" ".join(cur).split()) >= 230:
            out.append(" ".join(cur)); cur = []
    if cur: out.append(" ".join(cur))
    return [c for c in out if len(c.split()) >= CHUNK_MIN_WORDS]

def sections(text):
    """Yield (title, body) per top-level ## header, merging ## I/II chapter splits
    into their parent story."""
    parts = re.split(r"\n##\s+", "\n" + text)
    cur_title, cur_body = None, []
    for part in parts:
        if not part.strip(): continue
        line, _, rest = part.partition("\n")
        title = line.strip()
        # chapter markers (I, II, roman numerals, single letters) belong to prev story
        if re.fullmatch(r"[IVXLC]+|\d+|[A-Z]|-\s.*", title):
            cur_body.append(rest); continue
        if cur_title is not None:
            yield cur_title, "\n".join(cur_body)
        cur_title, cur_body = title, [rest]
    if cur_title is not None:
        yield cur_title, "\n".join(cur_body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cap", type=int, default=2000,
                    help="seeded random sample to ~eschaton scale (validated regime)")
    args = ap.parse_args()

    text = SRC.read_text(encoding="utf-8", errors="ignore")
    kept, dropped_slur, skipped, blocked = [], 0, [], []
    stories_used = []
    for title, body in sections(text):
        tl = title.lower().replace("’", "'").strip()
        bk = block_key(title)
        if tl in SKIP_TITLES:
            skipped.append(title); continue
        if bk in BLOCK_TITLES:
            blocked.append(title); continue
        n_before = len(kept)
        for raw in re.split(r"\n\s*\n", body):
            p = norm(raw)
            if not p or p.startswith("#"): continue
            if re.match(r"^Published\b.*\b(in|Stories|Magazine|Vol\.)", p) or re.match(r"^\(?(First |Originally )?[Pp]ublished", p):
                continue  # publication metadata, not prose
            for chunk in split_long(p):
                if len(chunk.split()) < CHUNK_MIN_WORDS: continue
                if SLUR.search(chunk):
                    dropped_slur += 1; continue
                k = hkey(chunk)
                if k in DEDUP: continue
                DEDUP.add(k)
                kept.append(chunk)
        if len(kept) > n_before:
            stories_used.append((title, len(kept) - n_before))

    if args.cap and len(kept) > args.cap:
        import random
        random.Random(1937).shuffle(kept)   # HPL's death year, as the seed
        kept = kept[:args.cap]

    print("=== nyarlathotep corpus build (cosmic-horror register) ===")
    print(f"[kept]    {len(kept)} chunks (capped {args.cap}) from {len(stories_used)} stories")
    print(f"[blocked] {len(blocked)} racist-premise stories dropped whole: {blocked}")
    print(f"[slur]    {dropped_slur} chunks dropped by slur/term filter")
    print(f"[skipped] {len(skipped)} apparatus/non-fiction sections")
    lens = [len(c.split()) for c in kept]
    if lens:
        print(f"[len]     words min {min(lens)} med {int(statistics.median(lens))} max {max(lens)}")
    print("\n=== top stories by chunk count ===")
    for t, n in sorted(stories_used, key=lambda x: -x[1])[:12]:
        print(f"  {n:4d}  {t}")
    print("\n=== register spot-check (first 90 chars, 4 chunks) ===")
    for c in kept[:4]:
        print(f"  · {c[:90]}…")

    if args.dry_run:
        print("\n[dry-run] no file written"); return
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "nyarlathotep-v1-completion.jsonl"
    out.write_text("\n".join(json.dumps({"text": c}, ensure_ascii=False) for c in kept) + "\n")
    print(f"\nWROTE {len(kept)} records -> {out}")

if __name__ == "__main__":
    main()
