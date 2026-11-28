"""Write a read-only report for every translation workflow edition."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
import json
from pathlib import Path

from translation_backlog import audit, english_history, git, markdown_blobs
from translation_matrix import LANGUAGES


def commit_at(ref):
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()


def review_edition(locale, revision, source, history):
    localized = markdown_blobs(revision)
    findings = audit(locale, source, localized, history, detailed=True, checkpoint_ref=revision)
    return {
        "commit": revision,
        "markdown_files": len(localized),
        "counts": {name: len(paths) for name, paths in findings.items()},
        "findings": findings,
    }


def audit_editions(source_ref, locales, *, workers=3):
    source_commit = commit_at(source_ref)
    revisions = [commit_at(f"refs/remotes/origin/{locale}") for locale in locales]
    source = markdown_blobs(source_commit)
    history = english_history(source_commit)
    if workers == 1:
        reports = [review_edition(locale, revision, source, history) for locale, revision in zip(locales, revisions)]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            reports = list(pool.map(review_edition, locales, revisions, repeat(source), repeat(history)))
    return {
        "english_source_commit": source_commit,
        "english_markdown_files": len(source),
        "languages": dict(zip(locales, reports)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", default="refs/remotes/origin/master")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_editions(args.source_ref, tuple(locale for _, locale in LANGUAGES))
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Audited {len(report['languages'])} locales against {report['english_source_commit']}")


if __name__ == "__main__":
    main()
