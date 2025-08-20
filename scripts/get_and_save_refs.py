#!/usr/bin/env python3
import json
import re
from pathlib import Path

SRC_DIR = Path("./src")
REFS_JSON = Path("/tmp/refs.json")

# Matches content between {{#ref}} and {{#endref}}, including newlines, lazily
REF_RE = re.compile(r"{{#ref}}\s*([\s\S]*?)\s*{{#endref}}", re.MULTILINE)

def extract_refs(text: str):
    """Return a list of refs (trimmed) in appearance order."""
    return [m.strip() for m in REF_RE.findall(text)]

def main():
    if not SRC_DIR.is_dir():
        raise SystemExit(f"Not a directory: {SRC_DIR}")

    refs_per_path = {}  # { "relative/path.md": [ref1, ref2, ...] }

    for md_path in sorted(SRC_DIR.rglob("*.md")):
        rel = md_path.relative_to(SRC_DIR).as_posix()
        try:
            content = md_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Fallback if encoding is odd
            content = md_path.read_text(errors="replace")

        refs = extract_refs(content)
        refs_per_path[rel] = refs  # keep order from findall


    REFS_JSON.write_text(json.dumps(refs_per_path, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {REFS_JSON} with {len(refs_per_path)} files.")

if __name__ == "__main__":
    main()
