"""Write a read-only report for every translation workflow edition."""

import argparse
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
import json
from pathlib import Path

from translation_backlog import audit, english_history, git, load_state, markdown_blobs, planned_paths
from translation_matrix import LANGUAGES


def commit_at(ref):
    return git("rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()


def review_edition(locale, revision, source, history, initial_ref):
    localized = markdown_blobs(revision)
    findings = audit(locale, source, localized, history, detailed=True, checkpoint_ref=revision)
    state = load_state(revision, localized.keys(), initial_ref)
    planned = set(planned_paths(source, state, findings))
    unverified = set(findings["checkpoint_unverified"])
    review_only = {}
    for category in ("partly_untranslated", "untranslated_headings", "untranslated_reader_labels"):
        for path in findings[category]:
            if path not in planned:
                entry = review_only.setdefault(path, {
                    "checkpoint": "legacy_baseline" if path in unverified else "recorded_source",
                    "findings": [],
                })
                entry["findings"].append(category)
    findings["outside_translation_plan"] = review_only
    return {
        "commit": revision,
        "markdown_files": len(localized),
        "planned_markdown_files": len(planned),
        "counts": {name: len(paths) for name, paths in findings.items()},
        "findings": findings,
    }


def audit_editions(source_ref, locales, *, workers=3, initial_ref=None):
    source_commit = commit_at(source_ref)
    revisions = [commit_at(f"refs/remotes/origin/{locale}") for locale in locales]
    source = markdown_blobs(source_commit)
    history = english_history(source_commit)
    work = (locales, revisions, repeat(source), repeat(history), repeat(initial_ref))
    if workers == 1:
        reports = list(map(review_edition, *work))
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            reports = list(pool.map(review_edition, *work))
    return {
        "english_source_commit": source_commit,
        "english_markdown_files": len(source),
        "languages": dict(zip(locales, reports)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", default="refs/remotes/origin/master")
    parser.add_argument("--initial-source-ref", help="English baseline for legacy language branches")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_editions(args.source_ref, tuple(locale for _, locale in LANGUAGES), initial_ref=args.initial_source_ref)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Audited {len(report['languages'])} locales against {report['english_source_commit']}")


if __name__ == "__main__":
    main()
