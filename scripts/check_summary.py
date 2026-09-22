#!/usr/bin/env python3
"""Validate src/SUMMARY.md before mdbook ever sees it.

mdbook aborts the whole build on a malformed SUMMARY.md, and because every
language job rebuilds the book, a single bad line takes down the English site
and all 16 translated deploys at once. The two failure modes that have actually
bitten us:

  * the same file listed twice -> "Duplicate file in SUMMARY.md"
  * an entry pointing at a file that does not exist -> fails because book.toml
    sets `create-missing = false`

Run with --fix to drop duplicate entries (only the safe, childless ones).
"""

import argparse
import re
import sys
from pathlib import Path

SUMMARY = Path("src/SUMMARY.md")

# - [Title](some/path.md)   /   indented variants for nested entries
ENTRY_RE = re.compile(r"^(?P<indent>\s*)[-*]\s+\[(?P<title>.*?)\]\((?P<link>[^)]*)\)\s*$")


def indent_width(s: str) -> int:
    return len(s.expandtabs(4))


def parse(lines):
    """Yield (index, indent, title, link) for every real page entry.

    Draft entries -- `[Title]()` with an empty link, used for the external
    HackTricks links -- are skipped: mdbook allows any number of those.
    """
    for i, line in enumerate(lines):
        m = ENTRY_RE.match(line)
        if not m:
            continue
        link = m.group("link").strip()
        if not link:
            continue
        if link.startswith(("http://", "https://", "#", "mailto:")):
            continue
        yield i, indent_width(m.group("indent")), m.group("title"), link


def has_children(lines, idx, indent):
    """True if the next entry is nested under the one at idx."""
    for j in range(idx + 1, len(lines)):
        if not lines[j].strip():
            continue
        m = ENTRY_RE.match(lines[j])
        if not m:
            return False
        return indent_width(m.group("indent")) > indent
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true",
                    help="remove duplicate entries in place (keeps the first occurrence)")
    ap.add_argument("--summary", default=str(SUMMARY), help="path to SUMMARY.md")
    ap.add_argument("--skip-missing", action="store_true",
                    help="only check for duplicates, not for missing target files")
    args = ap.parse_args()

    path = Path(args.summary)
    if not path.is_file():
        print(f"error: {path} not found (run from the repo root)", file=sys.stderr)
        return 2

    src_dir = path.parent
    lines = path.read_text(encoding="utf-8").split("\n")
    entries = list(parse(lines))

    # --- duplicates -------------------------------------------------------
    first_seen = {}
    dupes = []          # (idx, indent, title, link, first_idx)
    for idx, indent, title, link in entries:
        if link in first_seen:
            dupes.append((idx, indent, title, link, first_seen[link]))
        else:
            first_seen[link] = idx

    # --- missing targets --------------------------------------------------
    missing = []
    if not args.skip_missing:
        for idx, _indent, title, link in entries:
            target = link.split("#", 1)[0]
            if target and not (src_dir / target).is_file():
                missing.append((idx, title, target))

    if not dupes and not missing:
        print(f"SUMMARY.md OK - {len(entries)} entries, no duplicates, no missing files.")
        return 0

    exit_code = 0

    if dupes:
        print(f"Found {len(dupes)} duplicate entr{'y' if len(dupes) == 1 else 'ies'} "
              f"in {path} (mdbook fails with 'Duplicate file in SUMMARY.md'):")
        for idx, _indent, title, link, first_idx in dupes:
            print(f"  line {idx + 1}: [{title}]({link})")
            print(f"           first listed on line {first_idx + 1}")

        if args.fix:
            removable = [d for d in dupes if not has_children(lines, d[0], d[1])]
            skipped = [d for d in dupes if d not in removable]
            for idx, *_ in sorted(removable, key=lambda d: -d[0]):
                del lines[idx]
            if removable:
                path.write_text("\n".join(lines), encoding="utf-8")
                print(f"\nRemoved {len(removable)} duplicate line(s) from {path}.")
            for idx, _indent, title, link, _f in skipped:
                print(f"\nNOT removed (line {idx + 1} has nested entries under it, "
                      f"so dropping it would orphan them): [{title}]({link})")
                print("  Resolve this one by hand.")
                exit_code = 1
        else:
            print("\nFix with: python3 scripts/check_summary.py --fix")
            exit_code = 1

    if missing:
        print(f"\nFound {len(missing)} entr{'y' if len(missing) == 1 else 'ies'} pointing at "
              f"files that do not exist (book.toml sets create-missing = false):")
        for idx, title, target in missing:
            print(f"  line {idx + 1}: [{title}]({target})")
        print("\nEither add the file or remove the entry - this is not auto-fixable,")
        print("since deleting the line could silently drop a page that should exist.")
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
