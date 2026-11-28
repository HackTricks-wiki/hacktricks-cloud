#!/usr/bin/env python3
"""Track which English source blobs have been translated on a language branch.

The language branches do not share ancestry with master, so comparing their
Markdown contents cannot tell whether translated prose is current. Each branch
instead records the Git blob ID of every English page it has translated.
"""

import argparse
import json
import os
import posixpath
import re
import subprocess
from io import BytesIO
from pathlib import Path
from urllib.parse import unquote, urlsplit

from translation_quality import (
    MARKDOWN, chapter_title, check_rendered_anchor_collisions, check_rendered_sidebar, copied_prose, copied_sentence, english_segments, markdown_problems, preserve_source_heading_anchors, summary_language_text, summary_parts, summary_structure,
    unchanged_summary_label, wrong_language,
)


SUMMARY_PATH = "src/SUMMARY.md"
STATE_PATH = Path(".translation-source-blobs.json")
# The last Translate All run that succeeded for every language, before the
# large AWS/Azure/GCP technique PRs were merged.
INITIAL_SOURCE_REF = "b9b85d019e2997ee1ca34fea60ec38d780aa3d9b"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def markdown_blobs(ref: str) -> dict[str, str]:
    result = {}
    for entry in git("ls-tree", "-rz", ref, "--", "src").split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        if path.endswith(".md"):
            result[path] = metadata.split()[2].decode("ascii")
    return result


def read_checkpoint(branch):
    try:
        state_json = subprocess.check_output(
            ["git", "show", f"{branch}:{STATE_PATH}"], stderr=subprocess.DEVNULL
        )
        state = json.loads(state_json.decode("utf-8"))
    except subprocess.CalledProcessError:
        return None
    if not isinstance(state, dict) or state.get("schema") != 1 or not isinstance(state.get("sources"), dict):
        raise ValueError(f"Invalid translation state on {branch}")
    return state


def recorded_sources(branch: str) -> dict[str, str] | None:
    checkpoint = read_checkpoint(branch)
    return checkpoint["sources"] if checkpoint is not None else None


def checkpoint_for_update(branch, initial_ref=None):
    checkpoint = read_checkpoint(branch)
    if checkpoint is not None:
        return checkpoint["sources"], checkpoint.get("assumed_baseline")
    baseline = git("rev-parse", "--verify", f"{initial_ref or INITIAL_SOURCE_REF}^{{commit}}").decode().strip()
    return {}, baseline


def load_state(branch: str, existing_files: set[str], initial_ref=None) -> dict[str, str]:
    recorded, baseline = checkpoint_for_update(branch, initial_ref)
    # An inferred legacy baseline is sufficient for planning, but stays
    # separate from the recorded source blobs used for audits and repairs.
    legacy = {
        path: blob for path, blob in markdown_blobs(baseline).items()
        if path in existing_files and path != SUMMARY_PATH
    } if baseline else {}
    return legacy | recorded


def extra_paths(args: argparse.Namespace) -> set[str]:
    values = []
    if args.extras:
        values.append(Path(args.extras).read_text(encoding="utf-8"))
    if args.extra_env:
        values.append(os.environ.get(args.extra_env, ""))
    return {path.strip() for value in values for path in re.split(r"[,\n]", value) if path.strip()}


def read_blobs(blob_ids):
    """Read many blobs with one Git process, with no checkout."""
    ids = sorted(set(blob_ids))
    if not ids:
        return {}
    raw = subprocess.check_output(
        ["git", "cat-file", "--batch"], input=("\n".join(ids) + "\n").encode("ascii")
    )
    stream = BytesIO(raw)
    result = {}
    for blob in ids:
        header = stream.readline().split()
        if len(header) != 3 or header[0].decode("ascii") != blob or header[1] != b"blob":
            raise RuntimeError(f"Cannot read translation blob {blob}")
        result[blob] = stream.read(int(header[2])).decode("utf-8", errors="replace")
        stream.read(1)  # The delimiter after the blob.
    return result


def english_history(source_ref):
    return set(git("rev-list", "--objects", "--no-object-names", source_ref, "--", "src").decode("ascii").splitlines())


def verified_source_blobs(branch, source, existing, historical_blobs):
    return {
        path: blob for path, blob in (recorded_sources(branch) or {}).items()
        if path in source and path in existing and blob in historical_blobs
    }


def audit(branch, source, existing, historical_blobs, *, detailed=False):
    missing = sorted(source.keys() - existing.keys())
    paths = sorted(source.keys() & existing.keys())
    comparable = verified_source_blobs(branch, source, existing, historical_blobs) if detailed else {}
    texts = read_blobs(
        [blob for path in paths for blob in (source[path], existing[path])]
        + list(comparable.values())
    )
    language = branch.rsplit('/', 1)[-1]
    copied, language_mismatches, navigation, partial = [], [], [], []
    structural_review = {}
    for path in paths:
        original, localized = texts[source[path]], texts[existing[path]]
        review_source = texts[comparable[path]] if path in comparable else original
        if path == SUMMARY_PATH:
            target = summary_parts(localized)
            source_parts = summary_parts(original)
            if summary_structure(source_parts) == summary_structure(target):
                if any(original_label is not None and unchanged_summary_label(original_label, localized_label)
                       for (_, original_label, _), (_, localized_label, _) in zip(source_parts, target)):
                    copied.append(path)
                elif wrong_language(summary_language_text(source_parts, target), language):
                    language_mismatches.append(path)
            else:
                navigation.append(path)
                if existing[path] in historical_blobs:
                    copied.append(path)
            continue
        if copied_prose(original, localized, majority=True) or (
            existing[path] in historical_blobs and english_segments(localized)
        ):
            copied.append(path)
        elif english_segments(original) and wrong_language(localized, language):
            language_mismatches.append(path)
        elif detailed and (copied_prose(review_source, localized) or copied_sentence(review_source, localized)):
            partial.append(path)
        if detailed and review_source != localized:
            problems = markdown_problems(review_source, localized, allow_source_aliases=True)
            if problems:
                structural_review[path] = problems
    report = {
        "missing": missing, "untranslated": copied, "wrong_language": language_mismatches,
        "navigation_structure": navigation,
    }
    if detailed:
        report.update(
            source_advanced=sorted(path for path, blob in comparable.items() if source[path] != blob),
            checkpoint_unverified=sorted(set(paths) - comparable.keys()),
            partly_untranslated=partial,
            structural_review=structural_review,
        )
    return report


def pending(branch: str, source_ref: str, extras: set[str], initial_ref=None) -> list[str]:
    source = markdown_blobs(source_ref)
    existing = markdown_blobs(branch)
    state = load_state(branch, existing.keys(), initial_ref)
    findings = audit(branch, source, existing, english_history(source_ref))
    repairs = {path for paths in findings.values() for path in paths}
    paths = (
        path for path, blob in source.items()
        if state.get(path) != blob or path in repairs or path in extras
    )
    return sorted(paths, key=lambda path: (path == SUMMARY_PATH, path))


def reusable_chapter_labels(summary, source_files, branch):
    """Reuse chapter translations for exact title links backed by a current source checkpoint."""
    recorded = recorded_sources(branch) or {}
    if not recorded:
        return {}
    existing = markdown_blobs(branch)
    entries = []
    for prefix, label, suffix in summary_parts(summary):
        if label is None or not suffix.startswith("]("):
            continue
        tokens = MARKDOWN.parseInline("[chapter" + suffix)[0].children or ()
        href = next((token.attrGet("href") for token in tokens if token.type == "link_open"), "")
        destination = urlsplit(href)
        if not destination.path or destination.scheme or destination.netloc or destination.query or destination.fragment:
            continue
        path = posixpath.normpath(posixpath.join("src", unquote(destination.path)))
        blob = source_files.get(path)
        if blob and recorded.get(path) == blob and path in existing:
            entries.append((prefix, label, suffix, blob, existing[path]))

    pages = read_blobs(blob for entry in entries for blob in entry[-2:])
    candidates = {}
    language = branch.rsplit("/", 1)[-1]
    for prefix, label, suffix, original, localized in entries:
        if chapter_title(pages[original]) != label:
            continue
        title = chapter_title(pages[localized])
        if not title or title == label or unchanged_summary_label(label, title) or wrong_language(title, language):
            continue
        parts = summary_parts(prefix + title + suffix)
        if len(parts) != 1 or parts[0] != (prefix, title, suffix):
            continue
        candidates.setdefault(label, set()).add(title)
    return {label: next(iter(titles)) for label, titles in candidates.items() if len(titles) == 1}


def restore_anchors(branch, source_ref):
    """Restore bookmarks in the build workspace from recorded source revisions."""
    if git("rev-parse", "HEAD") != git("rev-parse", branch):
        raise ValueError("The translation branch must be checked out before restoring anchors")
    if git("status", "--porcelain", "--untracked-files=no", "--", "src"):
        raise ValueError("The source directory must be clean before restoring anchors")

    existing = markdown_blobs(branch)
    checkpoints = verified_source_blobs(
        branch, markdown_blobs(source_ref), existing, english_history(source_ref)
    )
    checkpoints.pop(SUMMARY_PATH, None)
    originals = read_blobs(checkpoints.values())
    updated = []
    for path, blob in sorted(checkpoints.items()):
        page = Path(path)
        if page.is_symlink():
            continue
        localized = page.read_bytes().decode("utf-8")
        restored = preserve_source_heading_anchors(originals[blob], localized)
        if restored != localized:
            page.write_bytes(restored.encode("utf-8"))
            updated.append(path)
    return updated, len(checkpoints)


def record_translations(source_ref, paths, state, *, assumed_baseline=None, retain_removed=False):
    source = markdown_blobs(source_ref)
    for path in paths:
        if path not in source or not Path(path).is_file():
            raise RuntimeError(f"Translated page is missing: {path}")
        state[path] = source[path]
    checkpoint = {
        "schema": 1, "sources": {path: blob for path, blob in state.items() if retain_removed or path in source},
    }
    if assumed_baseline:
        checkpoint["assumed_baseline"] = assumed_baseline
    STATE_PATH.write_text(
        json.dumps(checkpoint, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Recorded {len(paths)} translated English source blobs")


def file_list(path: str) -> list[str]:
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("audit", "plan", "mark", "verify", "verify-render", "restore-anchors"))
    parser.add_argument("--language", required=True, help="Local or remote-tracking language branch")
    parser.add_argument("--source-ref", default="master")
    parser.add_argument("--initial-source-ref", help="English baseline for legacy language branches")
    parser.add_argument("--output", help="Newline-delimited output for plan")
    parser.add_argument("--file-list", help="Completed batch for mark")
    parser.add_argument("--extras", help="Comma- or newline-delimited paths to retry")
    parser.add_argument("--extra-env", help="Environment variable with comma-delimited paths")
    parser.add_argument("--toc", type=Path, help="Rendered mdBook sidebar, for verify-render")
    parser.add_argument("--detailed", action="store_true",
                        help="Include mixed-prose and Markdown differences in the read-only audit")
    args = parser.parse_args()
    if args.detailed and args.action != "audit":
        parser.error("--detailed is only supported by audit")

    if args.action == "audit":
        print(json.dumps(audit(
            args.language, markdown_blobs(args.source_ref), markdown_blobs(args.language),
            english_history(args.source_ref), detailed=args.detailed,
        ), indent=2, ensure_ascii=False))
    elif args.action == "restore-anchors":
        updated, eligible = restore_anchors(args.language, args.source_ref)
        print(f"{args.language}: restored source bookmarks in {len(updated)} of {eligible} checkpointed pages")
    elif args.action == "verify-render":
        if args.toc is None:
            parser.error("verify-render requires --toc")
        try:
            check_rendered_sidebar(
                Path(SUMMARY_PATH).read_text(encoding="utf-8"), args.toc.read_text(encoding="utf-8"), args.language,
            )
            check_rendered_anchor_collisions(args.toc.parent)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(f"{args.language}: rendered sidebar matches localized SUMMARY.md")
    elif args.action == "plan":
        if not args.output:
            parser.error("plan requires --output")
        paths = pending(args.language, args.source_ref, extra_paths(args), args.initial_source_ref)
        Path(args.output).write_text("".join(f"{path}\n" for path in paths), encoding="utf-8")
        print(f"{args.language}: {len(paths)} English pages pending translation")
    elif args.action == "mark":
        if not args.file_list:
            parser.error("mark requires --file-list")
        if git("rev-parse", "--abbrev-ref", "HEAD").decode().strip() != args.language:
            raise RuntimeError(f"mark must run on {args.language}")
        state, baseline = checkpoint_for_update(args.language, args.initial_source_ref)
        record_translations(args.source_ref, file_list(args.file_list), state, assumed_baseline=baseline)
    else:
        paths = pending(args.language, args.source_ref, set(), args.initial_source_ref)
        if paths:
            raise SystemExit(f"{args.language}: {len(paths)} pages still pending; first: {paths[:10]}")
        print(f"{args.language}: no pending translations for {args.source_ref}")


if __name__ == "__main__":
    main()
