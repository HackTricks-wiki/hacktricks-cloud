#!/usr/bin/env python3
"""Validate and synchronize the four canonical HackTricks Cloud categorization files.

No cloud credentials, network calls, or technique execution are involved.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import pprint
import re
import subprocess
import string

import yaml

PROVIDERS = ('aws', 'gcp', 'azure', 'k8s')
LEVELS = ('low', 'medium', 'high', 'critical')
FIELDS = {'verb', 'resource', 'subresource', 'group', 'full', 'namespace', 'name',
          'path', 'non_resource_url', 'mode', 'delegated_verb'}


def validate_match(match):
    if not isinstance(match, dict):
        raise ValueError('A match must be a mapping')
    if set(match) == {'always'} and isinstance(match['always'], bool):
        return
    for key in ('all', 'any'):
        if set(match) == {key} and isinstance(match[key], list):
            for child in match[key]:
                validate_match(child)
            return
    if set(match) == {'not'}:
        validate_match(match['not'])
        return
    if match.get('field') not in FIELDS:
        raise ValueError('Unknown Kubernetes match field')
    op = match.get('op')
    if op == 'truthy' and set(match) == {'field', 'op'}:
        return
    if set(match) != {'field', 'op', 'value'}:
        raise ValueError('Invalid match keys')
    value = match['value']
    if op in ('eq', 'ne', 'contains') and isinstance(value, str):
        return
    if op in ('prefix', 'suffix') and isinstance(value, str):
        return
    if op in ('in', 'not_in', 'prefix', 'suffix') and isinstance(value, list) and all(isinstance(v, str) for v in value):
        return
    raise ValueError('Unsupported match operation or value')


def validate(data, provider):
    if not isinstance(data, dict) or data.get('version') != 1 or data.get('provider') != provider:
        raise ValueError(f'Unsupported {provider} categorization schema')
    if provider == 'k8s':
        rules = data.get('rules')
        if not isinstance(rules, list) or not rules or rules[-1].get('match') != {'always': True}:
            raise ValueError('Kubernetes requires ordered rules and a final fallback')
        ids = set()
        for rule in rules:
            if not isinstance(rule.get('id'), str) or rule['id'] in ids:
                raise ValueError('Kubernetes rule IDs must be unique strings')
            ids.add(rule['id'])
            validate_match(rule['match'])
            if rule.get('severity') not in (*LEVELS, 'delegated'):
                raise ValueError('Invalid Kubernetes severity')
            if rule['severity'] == 'delegated':
                levels = rule.get('delegated_severities', {})
                if set(levels) != set(LEVELS) or any(v not in LEVELS for v in levels.values()):
                    raise ValueError('Invalid delegated severity map')
            if 'severity_when' in rule:
                conditional = rule['severity_when']
                validate_match(conditional['match'])
                if conditional['severity'] not in LEVELS:
                    raise ValueError('Invalid conditional severity')
            for _, field, spec, conversion in string.Formatter().parse(rule['description']):
                if field is not None and (field not in FIELDS or spec or conversion):
                    raise ValueError('Unsupported description placeholder')
        return
    categories = data.get('permission_categories', {})
    if set(categories) != set(LEVELS):
        raise ValueError('Expected all four permission categories')
    seen = {}
    for level, permissions in categories.items():
        if not isinstance(permissions, list):
            raise ValueError('Categories must contain permission lists')
        for permission in permissions:
            if not isinstance(permission, str) or not permission.strip():
                raise ValueError('Permissions must be nonempty strings')
            normalized = permission.casefold() if provider in ('aws', 'azure') else permission
            if normalized in seen and seen[normalized] != level:
                raise ValueError(f'Duplicate permission: {permission}')
            seen[normalized] = level
    for permission, level in data.get('severity_overrides', {}).items():
        normalized = permission.casefold() if provider in ('aws', 'azure') else permission
        if level not in LEVELS or (normalized in seen and seen[normalized] != level):
            raise ValueError(f'Override and category disagree: {permission}')
    for level in ('critical', 'high'):
        combinations = data.get('combinations', {}).get(level)
        if not isinstance(combinations, list):
            raise ValueError('Missing permission combinations')
        for combo in combinations:
            if not isinstance(combo, list) or not combo or any(not isinstance(p, str) or not p.strip() for p in combo):
                raise ValueError('Invalid permission combination')
    for key, values in data.items():
        if key.endswith('_regex'):
            for expression in (values if isinstance(values, list) else [values]):
                re.compile(expression)


def sync(book_root: Path, target: Path, *, check=False, validate_only=False):
    source = book_root / 'src/permission-categorizations'
    contents = {p: (source / f'{p}.yaml').read_bytes() for p in PROVIDERS}
    data = {p: yaml.safe_load(contents[p]) for p in PROVIDERS}
    for provider in PROVIDERS:
        validate(data[provider], provider)
    if validate_only:
        return
    cloud = (target / 'src/CloudPEASS/permission_risk_classifier.py').is_file()
    if not cloud and not (target / 'scripts/cloud_permission_risks.py').is_file():
        raise ValueError('Target must be CloudPEASS or Blue-CloudPEASS')
    rules_dir = target / ('src/CloudPEASS/risk_rules' if cloud else 'risk_rules')
    outputs = {rules_dir / f'{p}.yaml': contents[p] for p in PROVIDERS}
    for provider in PROVIDERS[:3]:
        if cloud:
            path = target / f'src/sensitive_permissions/{provider}.py'
            original = path.read_text()
            lines = original.splitlines(keepends=True)
            replacements = []
            names = {'very_sensitive_combinations': 'critical', 'sensitive_combinations': 'high'}
            for node in ast.parse(original).body:
                if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in names:
                    name = node.targets[0].id
                    replacements.append((node.lineno - 1, node.end_lineno,
                                         name + ' = ' + pprint.pformat(data[provider]['combinations'][names[name]], width=100) + '\n'))
            if len(replacements) != 2:
                raise ValueError(f'Missing legacy combination assignments: {path}')
            # Keep existing formatting when the literal value has not changed.
            for start, end, text in sorted(replacements, reverse=True):
                old = ast.literal_eval(ast.parse(''.join(lines[start:end])).body[0].value)
                level = names[ast.parse(text).body[0].targets[0].id]
                if old != data[provider]['combinations'][level]:
                    lines[start:end] = [text]
            outputs[path] = ''.join(lines).encode()
        else:
            outputs[target / f'{provider}_permissions_cat.yaml'] = yaml.safe_dump(
                data[provider]['permission_categories'], sort_keys=False, width=120).encode()
    hashes = {f'{p}.yaml': hashlib.sha256(contents[p]).hexdigest() for p in PROVIDERS}
    manifest_path = rules_dir / 'hacktricks-source.json'
    prior = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if prior.get('sha256') == hashes:
        manifest = prior  # Unrelated book commits must not create update commits.
    else:
        revision = subprocess.check_output(['git', '-C', str(book_root), 'rev-parse', 'HEAD'], text=True).strip()
        manifest = dict(repository='HackTricks-wiki/hacktricks-cloud', revision=revision,
                        path='src/permission-categorizations', sha256=hashes)
    outputs[manifest_path] = (json.dumps(manifest, indent=2) + '\n').encode()
    stale = [path for path, content in outputs.items() if not path.exists() or path.read_bytes() != content]
    if check and stale:
        raise ValueError('Stale canonical permissions: ' + ', '.join(str(p.relative_to(target)) for p in stale))
    if not check:
        for path in stale:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(outputs[path])
    print(f'{len(stale)} files {"need synchronization" if check else "updated"}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--book-root', type=Path, required=True)
    parser.add_argument('--target-root', type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    sync(args.book_root, args.target_root, check=args.check, validate_only=args.validate_only)


if __name__ == '__main__':
    main()
