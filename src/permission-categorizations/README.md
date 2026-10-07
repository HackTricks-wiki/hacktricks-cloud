# Permission risk categorizations

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud maintains the shared permission severity data consumed by [CloudPEASS](https://github.com/peass-ng/CloudPEASS) and [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edit the canonical platform file here, rather than the generated copies in either consumer.

- **Critical**: permissions that directly, or almost independently, grant powerful privileges, mint an identity, or enable privileged execution.
- **High**: access to sensitive information, credentials, or a conditional privilege escalation path.
- **Medium**: DoS/Break, operational disruption, ordinary changes, or conditional capabilities without a demonstrated sensitive-data or privilege path.
- **Low**: ordinary discovery and metadata access.

There is one canonical YAML file per platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), and [Kubernetes](k8s.yaml). These are machine-readable files; the platform pages display their complete YAML in the browser and explain how to edit them. The inline viewer uses the book’s copy, while the PEASS workflows fetch the canonical files from GitHub.

## Cloud provider files

`version` and `provider` identify the schema. `permission_categories` holds the four individual permission lists. Move a permission between lists to change its rating. AWS and Azure matching ignore case; GCP matching preserves case. Case aliases may repeat within the same severity, but conflicting ratings are rejected.

`severity_overrides` contains audited exceptions to generic rules. If an exception also appears in the catalog, both entries must agree. `severity_caps` prevents a combination from upgrading selected permissions. `non_permission_identifiers` excludes documented API-method names, condition keys, and other strings that are not actual authorization permissions.

`combinations.critical` and `combinations.high` are lists of permission lists: every element of an inner list must be granted for that combination to apply. Keep combinations together; splitting them into individual grants would overstate risk. Existing exact and regular-expression fields remain the fallback for permissions absent from the catalog. A full classifier rewrite or new matching behavior still requires code changes in the consumers.

## Kubernetes file

`rules` is ordered: the first matching rule wins. Each rule has a unique `id`, a `match`, a `severity`, and a plain-language `description`. Add a more specific rule before a broader one, or change an existing rule's severity. Preserve the final unconditional fallback.

Matches use `all`, `any`, and `not` for composition, or a `field`, `op`, and `value` comparison. Available fields are `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode`, and `delegated_verb`. Operations are `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, and `truthy` (no value required). `always: true` matches everything. Group, resource, subresource, and verb values are lowercase. A literal wildcard is written as `'*'`; matching a wildcard grant is explicit in the rules, rather than shell pattern expansion.

`severity_when` optionally selects another severity for a matching condition. `severity: delegated` is reserved for constrained impersonation: its `delegated_severities` map converts the delegated action's classification into the conditional rating. Description placeholders can reference the available fields, such as `{full}` and `{verb}`. The rules are data and never evaluated as Python or shell code.

## Validation and synchronization

Run `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` with PyYAML installed before submitting changes. The book's pull-request workflow runs the same validation.

Every Monday, both consumer repositories check out the current `master` of this book, validate all four files, compare SHA-256 hashes, and update their bundled YAML files and generated legacy lists. A source manifest records the book revision and each file's hash. Unrelated changes to the book produce no consumer commit. Each workflow also supports a manual run. Tests run before the workflow commits changed data to the consumer's default branch; failures leave that branch unchanged. The consumers continue using their bundled copies offline between updates.

To update locally in a consumer, run `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Add `--check` to detect stale copies without writing them.

Source fetching in both consumers retries five times with bounded checkout deadlines and increasing delays. Incomplete downloads stay in temporary directories; exhausted retries leave the existing bundled data unchanged.
{{#include ../banners/hacktricks-training.md}}
