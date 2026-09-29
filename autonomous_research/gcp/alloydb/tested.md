# AlloyDB security research

## 2026-09-28 — official-contract, role and local CLI audit

No AlloyDB resource was created or accessed. A read-only lab state check found the AlloyDB API disabled; the attempted list failed with `SERVICE_DISABLED`, the enable prompt was declined, and no API/service/resource state changed. The review otherwise used current stable REST/audit contracts, official workflow documentation, locally installed `gcloud alloydb` help and read-only predefined-role inspection.

### Retained post-exploitation techniques

- **Server-side export to attacker storage.** Raw REST requires `alloydb.clusters.export`; supported CLI/custom-role guidance adds `alloydb.clusters.get`. Cloud AlloyDB Viewer currently has both. The source P4SA needs only `storage.objects.create` on a destination bucket, which an attacker who owns that bucket can grant. No database credential or source-project Storage role is required.
- **Built-in administrator credential.** `alloydb.users.create`/`update` can plant or reset a password user and assign the managed `alloydbsuperuser` database role. This is broad database administration, not host/unrestricted PostgreSQL `SUPERUSER` or GCP IAM.
- **IAM user plus explicit database role.** IAM enrollment alone is not compromise: official docs say it has no non-`PUBLIC` database privileges by default. The retained chain explicitly assigns a useful database role and requires the controlled principal's separate IAM login/connectivity or Data API authority. Remote MCP additionally needs `mcp.tools.call`, IAM database auth and `dataApiAccess=ENABLED`; the default internal-only setting is sufficient for Studio, not MCP.
- **Data API/Studio SQL.** `executeSql*` crosses the caller's network boundary but does not bypass database authentication or PostgreSQL grants. `dataApiAccess` and the chosen built-in/IAM client path are explicit prerequisites. The remote MCP server is another client for this primitive, not a separate authorization finding.
- **Cross-project backup restore.** AlloyDB documents same-region restores into a different project. The book keeps destination `alloydb.clusters.create` and source `alloydb.backups.get` as the conservative two-resource boundary. Stable v1 currently omits the source permission from its REST page while the v1beta audit catalog lists it; only a private-first minimum-role test should determine whether that is documentation drift or an authorization defect.

### Persistence boundary

Four service-level primitives remain: API-managed built-in credential, conditional IAM database user, native PostgreSQL role/object below API inventory, and an external connection path combined with a standing credential. IAM enrollment does not survive revocation of its own IAM login role; public IP does not bypass database authentication; both bounds are now explicit.

### Material corrections and no-garbage decisions

- Added the missing Viewer-level `ExportCluster` exfiltration path and its P4SA/Storage boundary.
- Removed the false implication that an IAM database user automatically receives data privileges.
- Replaced "full/unrestricted superuser" language with the managed `alloydbsuperuser` boundary.
- Removed unsupported password-free Studio access: `executeSqlReadOnly` in Viewer still needs a valid database identity, object grants and a permitted Data API path.
- Removed network weakening from post-exploitation because its distinct value is persistence only when combined with a standing database credential.
- Removed deletion, fault injection, restart/failover, promotion and operation cancellation as standalone post-exploitation H3s. They are destructive/availability actions, recover no sensitive information and operation deletion does not erase the original audit record.
- Did not promote unauthenticated MCP `tools/list`: it exposes a static product schema, not victim resources, identities or data.
- Corrected exact audit classes: `ExportCluster` and `ExecuteSql*` are off-by-default Data Access; user/config/restore writes are always-on Admin Activity; direct PostgreSQL SQL is outside Cloud Audit Logs but not necessarily outside database, pgAudit, Query Insights or network telemetry.

### 2026-09-28 — independent reciprocal review

- Confirmed the export split: raw `ExportCluster` publishes only `clusters.export`, while supported workflow/custom-role guidance adds `clusters.get`; current Viewer has both. Object Creator is sufficient only for a new destination object; replacement additionally needs object deletion.
- Corrected MCP prerequisites to include `mcp.tools.call`, IAM database authentication, `dataApiAccess=ENABLED`, and the PostgreSQL 17 bound for the read-only MCP tool. Studio's Google-internal path and direct connectors remain distinct.
- Corrected the native PostgreSQL example. A managed `alloydbsuperuser` cannot generally transfer object ownership to `postgres`; the example now creates the durable object under the planted role and revokes the temporary membership from the initiating user.
- Identified the restore-version documentation mismatch: stable v1 publishes only destination authorization, while the v1beta audit catalog includes a source-backup check. The public book retains source authorization as a prerequisite; a live private-first test remains necessary to characterize enforcement and source-project telemetry. Restore stealth is rated High for a controlled cross-project destination because all guaranteed default records are there, not in the source project. No cloud state was touched.

### Validation

- Current local predefined-role contents were inspected for Admin, Viewer, Client, Database User and basic Editor.
- Stable local help was checked for user create, cluster export/restore and instance security flags.
- Book Bash/Python syntax, reference targets, numbered citations, details/fences, H3 metadata and external reference URLs were checked after editing.
