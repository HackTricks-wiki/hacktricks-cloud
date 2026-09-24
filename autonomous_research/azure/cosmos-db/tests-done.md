# Cosmos DB — Tests Done

Wiki: `az-cosmosdb-privesc.md` / post-exploitation, unauth `az-cosmosdb-unauth`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Restore-to-attacker-account exfil | `.../restore/action` (+ target acct) | DOC-ONLY |
| 2 | `dataTransferJobs` copy to attacker sink | `dataTransferJobs/write` | DOC-ONLY |
| 3 | CMK revocation ransom | `databaseAccounts/write`+KV | DOC-ONLY |
| 4 | Data-plane Users/Permissions **resource-token** persistence | data-plane | DOC-ONLY (separate plane = blind spot) |
| 5 | Throughput cost-DoS | `databaseAccounts/.../throughputSettings/write` | DOC-ONLY |
| 6 | `sqlRoleAssignments` native-RBAC self-grant (data-plane) | `sqlRoleAssignments/write` | DOC-ONLY (not in Activity Log) |

**Note:** Cosmos native (SQL) RBAC = separate plane, not in Activity Log = detection blind spot.
