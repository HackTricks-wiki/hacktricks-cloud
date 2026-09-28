# AlloyDB research checklist

## Completed documentation and local checks

- [x] Inspect current Admin, Viewer, Client, Database User and basic Editor role contents.
- [x] Separate AlloyDB IAM authorization from PostgreSQL user/object authorization.
- [x] Add Viewer-level `ExportCluster` exfiltration with caller, P4SA and destination-bucket bounds.
- [x] Correct built-in `alloydbsuperuser` versus unrestricted PostgreSQL host superuser language.
- [x] Correct IAM enrollment: no non-`PUBLIC` database privilege exists without an explicit role or
      PostgreSQL grant.
- [x] Bound Data API/Studio by database authentication, PostgreSQL grants and `dataApiAccess`.
- [x] Treat remote MCP as the same SQL primitive while recording its extra `mcp.tools.call`, IAM
      authentication, explicit Data API enablement and PostgreSQL-version boundaries.
- [x] Record the stable-v1/v1beta restore-permission documentation mismatch while retaining source
      authorization as the public-book prerequisite; preserve same-region and destination setup.
- [x] Separate durable credential/native-role/network paths from one-shot post-exploitation.
- [x] Remove destructive-only availability techniques and static unauthenticated MCP schema output.
- [x] Map current stable audit methods and downstream Storage/database telemetry.

## Safe future validation

- [ ] In a disposable synthetic cluster, grant a custom principal only `clusters.get` and
      `clusters.export`, grant the source P4SA object creation on a controlled bucket, and capture
      CSV/SQL export, Storage actor and LRO start/completion logs with Data Access off and on.
- [ ] Repeat raw REST export without `clusters.get` to separate API minimum from `gcloud` helper
      discovery/polling. Remove the object, bucket grant and every temporary principal afterward.
- [ ] Create built-in and IAM users with/without `--db-roles`, verify exact resulting PostgreSQL
      memberships and managed `alloydbsuperuser` limits, then delete every user/native object.
- [ ] Compare password and IAM `ExecuteSql`/`ExecuteSqlReadOnly` through client library, Studio and
      remote MCP with `dataApiAccess` default, enabled and disabled. Capture method/version,
      statement redaction, engine logs and Query Insights; never retain credentials or query data.
- [ ] For remote MCP, separately test absence/presence of `mcp.tools.call`, confirm IAM-only
      database authentication, and use PostgreSQL 17+ for `execute_sql_read_only`.
- [ ] Compare stable v1 and v1beta cross-project restore with destination-only `clusters.create`
      and no source `backups.get`, then invert the source permission. A successful destination-only
      copy is a private security finding; do not publish it before coordinated reporting.
- [ ] Confirm whether any separate source-project record (including `GetBackup`) is emitted and
      which project receives `RestoreCluster`, service-agent, instance and database-user events.
      Delete the restored cluster/instance, source backup,
      users, network grants and service-agent grants.
- [ ] Verify whether native PostgreSQL roles created through SQL appear in the AlloyDB Users API and
      which catalog/logging controls reliably identify `SECURITY DEFINER` or event-trigger residue.

## Cleanup invariant

- [ ] Snapshot full instance connectivity/SSL/Data API/database-flag state and every affected user
      role before mutation; restore complete arrays/maps rather than overwriting concurrent state.
- [ ] Delete export objects, destination buckets if created, restored clusters/instances, backups,
      API/native users, database objects and all P4SA/IAM grants.
- [ ] Wait for every AlloyDB LRO to terminate, verify resource absence and return any initially
      disabled API to disabled.
