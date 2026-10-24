"""Regression tests for catalog source anchors."""
from scripts.validate_privesc_paths import source_errors


def test_source_errors_checks_techniques_and_exclusions(tmp_path):
    page = tmp_path / 'src' / 'page.md'
    page.parent.mkdir()
    page.write_text('### `--scopes=cloud-platform`\n### Secrets in etcd\n'
                    '```\n### Not a heading\n```\n', encoding='utf-8')
    catalog = tmp_path / 'src' / 'privilege-escalation-paths' / 'gcp'
    catalog.mkdir(parents=True)
    (catalog / 'techniques.yaml').write_text(
        '- source: src/page.md#--scopescloud-platform\n'
        '- source: src/page.md#scopescloud-platform\n', encoding='utf-8')
    (catalog / '_excluded.yaml').write_text(
        '- source: src/page.md#secrets-in-etcd\n'
        '- source: src/page.md#discover-secrets-in-etcd\n'
        '- source: src/page.md#not-a-heading\n', encoding='utf-8')
    errors = source_errors(tmp_path, catalog.parent)
    assert len(errors) == 3
    assert any('scopescloud-platform' in error for error in errors)
    assert any('discover-secrets-in-etcd' in error for error in errors)
    assert any('not-a-heading' in error for error in errors)


def test_source_errors_preserves_angle_brackets_in_inline_code(tmp_path):
    page = tmp_path / 'src' / 'page.md'
    page.parent.mkdir()
    page.write_text('## Pivot via `<send-request>`\n', encoding='utf-8')
    catalog = tmp_path / 'src' / 'privilege-escalation-paths' / 'azure'
    catalog.mkdir(parents=True)
    (catalog / '_excluded.yaml').write_text(
        '- source: src/page.md#pivot-via-send-request\n', encoding='utf-8')
    assert source_errors(tmp_path, catalog.parent) == []
