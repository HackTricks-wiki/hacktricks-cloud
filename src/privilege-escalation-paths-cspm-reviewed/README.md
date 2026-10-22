# Reviewed privilege escalation paths for CSPM

{{#include ../banners/hacktricks-training.md}}

This directory is the reviewed machine-readable technique set consumed by [Blue-CloudPEASS](https://github.com/peass-ng/PEASSo-CSPM). It is separate from the broader `src/privilege-escalation-paths` research catalog so new research stays available without creating unreviewed CSPM checks. Each active entry links to its HackTricks source page. Consumers fetch and validate this reviewed set weekly.

## Layout

There is one directory per platform and one YAML file per service, mirroring the HackTricks privilege-escalation pages: `aws/`, `gcp/`, `azure/` (including Entra ID) and `k8s/` (Kubernetes and OpenShift). For example `gcp/iam.yaml` holds the techniques documented in `gcp-iam-privesc.md`. One file per service keeps reviews small, avoids merge conflicts between contributors, and lets a page and its catalog file be updated in the same pull request.

- `<service>.yaml` is a YAML list of technique entries.
- `_excluded*.yaml` lists HackTricks techniques that were reviewed and intentionally not modelled as principal-to-principal edges (`source`, `technique`, `reason`), so reviewers can tell "not modelled" from "missed".
- `_todo.yaml` holds commented-out notes for techniques still being written.
- Comments are preserved verbatim by the consumers; use them for per-file modelling conventions.

## Entry format

The authoritative validator is `peaso/privesc/schema.py` in Blue-CloudPEASS; its JSON Schema is published next to this file as [`privesc-technique.schema.json`](privesc-technique.schema.json) for editor completion and quick checks.

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Unique kebab-case id prefixed by the provider (`aws-`, `gcp-`, `azure-`/`entra-`, `k8s-`). Never reuse or rename an id. |
| `provider` | yes | `aws`, `gcp`, `azure` or `k8s`; must match the directory. |
| `service` | yes | Service the technique abuses (usually the file name). |
| `title` | yes | Short description of the escalation. |
| `source` | yes | HackTricks Cloud page and heading anchor, `src/...md#anchor`. The page and anchor must exist. |
| `source_revision` | no | Book revision the source was verified against. |
| `summary` | yes | One or two sentences: what the source gains. No commands or how-to steps. |
| `requires` | yes | `all_of` (every requirement) and/or `any_of` (list of alternative requirement lists). Each requirement names an `action` (permission) and the `resource` it must cover, using placeholders such as `{target.arn}` or `{target.email}`. |
| `target` | yes | `kind` of the principal or entity gained, optional `selector` limiting candidate targets, `scope` and `aggregate_as` label. |
| `severity` | yes | `critical`, `high`, `medium`, `low` or `info`. |
| `mitigation` | yes | How defenders remove or constrain the path. |
| `confidence` | no | `derived`, `conditional` or `unknown`. |
| `conditions` | no | Facts the snapshot cannot prove (each with `id` and `description`); they make an edge conditional. |
| `blockers` | no | Controls that remove the edge when present (SCPs, deny policies, admission policies...). |
| `preconditions`, `source_kind`, `source_selector`, `pivot_resource_type` | no | Advanced modelling fields; see the schema. |
| `references`, `notes` | no | Extra URLs and reviewer notes. |

Unknown fields, unknown selector keys, unsupported target kinds or placeholders, and shell commands in prose are rejected (or flagged) because the evaluator would not understand them.

## Contributing

1. Document the technique on its HackTricks page first, under its own heading, and use that heading anchor as `source`.
2. Add or update the entry in `<provider>/<service>.yaml` (create the file if the service has none yet).
3. Validate with a Blue-CloudPEASS checkout and PyYAML installed:
   `python /path/to/Blue-CloudPEASS/scripts/sync_hacktricks_privesc.py --book-root . --validate-only`
4. Open a pull request. Removing an entry or changing its `id` needs a reviewed ledger entry in the consumer, so prefer fixing an entry over deleting it, and explain removals in the pull request.

## Synchronization

Every Monday Blue-CloudPEASS checks out the current `master` of this book, validates this directory, and compares SHA-256 hashes with the manifest recorded at its previous sync (`risk_rules/hacktricks-privesc-source.json`). Files changed only here are copied byte for byte; files changed only in the consumer are kept until they are upstreamed; files changed on both sides fail the sync for a human to resolve. Entries are never dropped from the consumer unless a reviewed ledger accepts the removal. Unrelated book commits produce no consumer commit.

{{#include ../banners/hacktricks-training.md}}
