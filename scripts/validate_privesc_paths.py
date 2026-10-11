#!/usr/bin/env python3
"""Validate src/privilege-escalation-paths before it is merged.

Layout: src/privilege-escalation-paths/<provider>/<service>.yaml (provider: aws, gcp, azure, k8s),
plus README.md and the exported JSON Schema at the directory root. scripts/privesc_paths_schema.py
is a copy of Blue-CloudPEASS peaso/privesc/schema.py, the evaluator's strict loader: it rejects
unknown fields, target kinds, selector keys and placeholders, duplicate ids, and `source` pages
that do not exist in this book. The JSON Schema must match the one the loader exports.

Usage: python scripts/validate_privesc_paths.py --book-root .   (requires PyYAML)
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

PATH = 'src/privilege-escalation-paths'
PROVIDERS = ('aws', 'gcp', 'azure', 'k8s')
FILE_NAME = re.compile(r'^_?[a-z0-9][a-z0-9_.-]*\.yaml$')
ROOT_EXTRAS = re.compile(r'^(README\.md|[A-Za-z0-9_.-]+\.schema\.json)$')
SCHEMA_FILE = 'privesc-technique.schema.json'


def layout_errors(root: Path):
    errors = []
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if path.is_symlink():
            errors.append(f'symbolic link not allowed: {rel.as_posix()}')
        elif path.is_dir():
            if len(rel.parts) > 1 or rel.parts[0] not in PROVIDERS:
                errors.append(f'unexpected directory: {rel.as_posix()}')
        elif len(rel.parts) == 1:
            if not ROOT_EXTRAS.match(rel.name):
                errors.append(f'unexpected file at the root: {rel.name}')
        elif len(rel.parts) == 2 and not FILE_NAME.match(rel.name):
            errors.append(f'catalog files must be lowercase <name>.yaml: {rel.as_posix()}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--book-root', type=Path, default=Path('.'))
    args = parser.parse_args()
    book = args.book_root.resolve()
    root = book / PATH
    spec = importlib.util.spec_from_file_location('privesc_paths_schema', book / 'scripts/privesc_paths_schema.py')
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)

    errors = layout_errors(root)
    result = schema.load_catalog(root, hacktricks_root=book)
    errors += result['errors']
    exported = json.dumps(schema.json_schema(), indent=2, sort_keys=True) + '\n'
    schema_path = root / SCHEMA_FILE
    if not schema_path.is_file() or schema_path.read_text() != exported:
        errors.append(f'{SCHEMA_FILE} is stale; regenerate it from scripts/privesc_paths_schema.py json_schema()')
    if errors:
        for error in errors[:50]:
            print(f'error: {error}', file=sys.stderr)
        if len(errors) > 50:
            print(f'... {len(errors) - 50} more errors', file=sys.stderr)
        return 1
    print(f"Privilege-escalation paths are valid: {len(result['files'])} files, "
          f"{len(result['entries'])} techniques, {result['excluded']} reviewed exclusions")
    return 0


if __name__ == '__main__':
    sys.exit(main())
