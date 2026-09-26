# AlloyDB — open questions

- [ ] If a suitable existing AlloyDB fixture becomes available, test `ExecuteSqlReadOnly` with `roles/alloydb.viewer` but no `alloydb.users.login` and no database account. The current v1 audit reference lists a login check, and Studio requires database authentication; do not claim viewer-only data access without a successful low-permission test.
- [ ] Verify whether the AlloyDB Studio execution method is available on a documented public REST route, or only through console/client-library transport. The v1 REST discovery list does not enumerate an `instances.executeSql` method, though the audit reference names the RPC.
