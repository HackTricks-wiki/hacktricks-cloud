# Privilege escalation paths

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud maintains the machine-readable privilege escalation catalog consumed by [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Each technique states which permissions a principal must effectively hold, and on which resources, to obtain the privileges of a set of target principals. Blue-CloudPEASS evaluates these entries offline against a read-only inventory snapshot and draws principal-to-principal attack paths, with the granting policy or binding as evidence and the mitigation that removes the path. Edit the canonical files here, rather than the copies in the consumer.

Entries describe preconditions, the reachable targets and the mitigation only. They contain no commands, payloads or execution steps; the linked HackTricks page explains the technique.

## Layout

There is one directory per platform (`aws`, `gcp`, `azure`, `k8s`) and one `<service>.yaml` file per service, each holding a YAML list of techniques. Files named `_excluded*.yaml` list reviewed HackTricks techniques that intentionally have no entry, such as post-exploitation, persistence or techniques that cannot be modelled from configuration, with the reason. `privesc-technique.schema.json` is the exported JSON Schema for editor completion and validation.

## Technique fields

- `id`: globally unique, lowercase and kebab-case, prefixed with the platform.
- `provider`, `service`, `title` and `summary`: one sentence describing what the source gains.
- `source`: the HackTricks page and anchor documenting the technique, relative to this book. `source_revision` is the book commit that was read.
- `requires`: the permissions the source must hold. `all_of` lists every required item, and `any_of` lists alternatives. AWS and GCP items use `action` and `resource`, Azure items use `action` (or `data_action`) and `scope`, Entra ID items use `entra_permission` or `entra_role`, and Kubernetes items use `verb`, `resource`, `subresource`, `api_group` and `namespace`. Placeholders such as `{target.arn}` bind a requirement to the target.
- `target`: the target `kind`, a `selector` whose conditions must all hold for a principal to be reachable, and its `scope`.
- `conditions` and `blockers`: what may prevent the path in practice, such as condition keys, SCPs, boundaries or admission policies.
- `confidence`, `severity`, `mitigation`, `references` and optional `notes`.

Unknown fields, target kinds, selector keys and placeholders are rejected rather than ignored, so an entry can never silently widen or narrow its target set. Add support for a new selector in the consumer evaluator first.

### Schema v2 joins

The v2 loader adds two placeholders and one AWS selector, and allows the existing K8s running-pod selector on GCP targets. These fields require an exact join to collected inventory; missing inventory yields unknown coverage, not a reachable path.

| Field | Use and required shape |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` and `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Use together on an AWS `aws_account_admin` target. Every requirement alternative must include `iam:CreatePolicyVersion` on that placeholder. The policy must be attached to a role the source can assume in the same account; the evaluator checks policy version capacity and recomputes the role's effective permissions. `SetDefaultPolicyVersion` is not covered. |
| `target.selector.k8s_sa_used_by_running_pod: true` | On a GCP `k8s_service_account` target with `scope: cluster`, selects KSAs used by running pods with an available token in the matched GKE cluster. Do not combine it with `k8s_sa_in_cluster` or `k8s_sa_has_token_secret`. Existing K8s use is unchanged. |
| `{source_rolebound_clusterrole}` | Use as `resource_name` on K8s `clusterroles` requirements with `api_group: rbac.authorization.k8s.io` and `namespace: "*"`. Each alternative needs `escalate` and `update` or `patch` on the same name. The target must be a `k8s_service_account` with `scope: same_namespace` and `selector.k8s_sa_in_namespace: "{target.namespace}"`; a RoleBinding must bind the source in that namespace. |

## Validation and synchronization

Run `python scripts/validate_privesc_paths.py --book-root .` with PyYAML installed before submitting changes. It checks the directory layout, every entry with the evaluator's strict loader (`scripts/privesc_paths_schema.py`, a copy of the Blue-CloudPEASS schema module), unique ids, source pages and heading anchors, and that the JSON Schema is current. Use `--peaso-root /path/to/Blue-CloudPEASS` to also compare both schema files byte-for-byte with the consumer. The book's pull-request workflow runs the same validation.

Every Monday, Blue-CloudPEASS checks out the current `master` of this book, validates these files, and compares each file's SHA-256 hash with the hashes recorded at the previous synchronization. Upstream additions, updates and deletions replace unchanged consumer copies. A file changed on both sides is reported as a conflict, and technique ids are never dropped without an explicit reviewed ledger. Invalid content or a failed test leaves the consumer's default branch unchanged. Unrelated changes to the book produce no consumer commit.
{{#include ../banners/hacktricks-training.md}}
