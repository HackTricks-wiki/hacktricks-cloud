#!/usr/bin/env python3
"""Check the shared layout and category rules for all cloud persistence pages."""

import re
from pathlib import Path


CATEGORIES = (
    "Standing access grants",
    "Reusable credentials",
    "Triggered execution",
    "Code and artifact backdoors",
    "Continuous data export",
    "Persistent defense evasion",
    "Self-healing and protected footholds",
)
ROOTS = (
    ("aws-security/aws-persistence", "aws-services"),
    ("gcp-security/gcp-persistence", "gcp-services"),
    ("azure-security/az-persistence", "az-services"),
)
LINKED_WALKTHROUGHS = (
    (
        "aws-security/aws-post-exploitation/aws-lambda-post-exploitation/"
        "aws-warm-lambda-persistence.md",
        "aws-services",
    ),
)
BANNER = re.compile(r"^\{\{#include [^\n]+hacktricks-training\.md\}\}\s*$", re.M)
BAD_PREFIX = re.compile(
    r"^(?:Persistence(?:\s*[:/—-]|\s+(?:via|through|in)\b)"
    r"|Post-exploitation\s*/\s*Persistence)",
    re.I,
)


def headings(text):
    """Read Markdown headings, excluding fenced and HTML preformatted code."""
    result = []
    fence = None
    preformatted = False
    for match in re.finditer(r"^.*(?:\n|$)", text, re.M):
        line = match.group().rstrip("\n")
        if preformatted:
            if "</pre>" in line:
                preformatted = False
            continue
        if fence is None and re.search(r"<pre(?:\s|>)", line):
            preformatted = "</pre>" not in line
            continue
        delimiter = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if delimiter:
            marker = delimiter[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        heading = re.match(r"^(#{1,6}) (.+)$", line)
        if heading:
            result.append((match.start(), match.end(), len(heading[1]), heading[2]))
    return result


def check_page(path, text, service_directory, overview=False):
    errors = []
    sections = headings(text)
    banner = BANNER.search(text)
    if not sections or sections[0][2] != 1 or text[:sections[0][0]].strip():
        errors.append("must start with a page title")
    if banner is None or len(sections) < 2:
        return errors + ["missing initial banner or service heading"]
    first = sections[1]
    service = first[3]
    if (
        first[2] != 2
        or first[0] < banner.end()
        or text[banner.end():first[0]].strip()
        or service in CATEGORIES
        or service in {"Summary", "Requirements", "References", "Persistence categories"}
        or "`" in service
        or BAD_PREFIX.match(service)
    ):
        errors.append("first heading after the banner must name the service")
    next_heading = sections[2][0] if len(sections) > 2 else len(text)
    introduction = text[first[1]:next_heading]
    enumeration = re.search(
        r"For service (?:information and )?enumeration, see:\s*"
        r"\{\{#ref\}\}\s*([^\n]+)\s*\{\{#endref\}\}",
        introduction,
    )
    if enumeration is None:
        errors.append("service heading must be followed by enumeration text and a reference")
    else:
        target = enumeration[1].strip()
        destination = (path.parent / target).resolve()
        if target.endswith("/"):
            destination /= "README.md"
        if service_directory not in destination.parts or not destination.is_file():
            errors.append(f"invalid service enumeration reference: {target}")

    for index, (start, end, level, title) in enumerate(sections):
        if level > 1 and BAD_PREFIX.match(title):
            errors.append(f"technique title has a redundant prefix: {title}")
        if title not in CATEGORIES:
            continue
        if level != 2:
            errors.append(f"category must use H2: {title}")
        stop = next(
            (item[0] for item in sections[index + 1:] if item[2] <= level), len(text)
        )
        children = sum(
            item[2] == 3 for item in sections[index + 1:] if item[0] < stop
        )
        if children == 0:
            children = len(re.findall(r"^- \*\*", text[end:stop], re.M))
        if children < 2:
            errors.append(f"category contains fewer than two techniques: {title}")

    if overview:
        for category in CATEGORIES:
            definition = f"- **{category}** —"
            if text.count(definition) != 1:
                errors.append(f"overview must define {category} exactly once")
    return errors


def main():
    source = Path("src/pentesting-cloud")
    total = 0
    failures = []
    for relative, service_directory in ROOTS:
        directory = source / relative
        files = sorted(directory.rglob("*.md"))
        if not files:
            failures.append(f"{directory}: no persistence pages found")
        for path in files:
            total += 1
            errors = check_page(
                path, path.read_text(), service_directory, path == directory / "README.md"
            )
            failures.extend(f"{path}: {error}" for error in errors)
    for relative, service_directory in LINKED_WALKTHROUGHS:
        path = source / relative
        if not path.is_file():
            failures.append(f"{path}: missing linked persistence walkthrough")
            continue
        total += 1
        errors = check_page(path, path.read_text(), service_directory)
        failures.extend(f"{path}: {error}" for error in errors)
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Persistence structure OK — {total} pages; no singleton categories or title prefixes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
