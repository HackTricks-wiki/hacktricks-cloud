# Cosmos DB — Tests Done

Wiki: `az-cosmosdb-privesc.md` / post-exploitation, unauth `az-cosmosdb-unauth`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Restore-to-attacker-account exfil | `.../restore/action` (+ target acct) | DOC-ONLY |
| 2 | `dataTransferJobs` copy to attacker sink | `dataTransferJobs/write` | DOC-ONLY |
| 3 | CMK revocation ransom | `databaseAccounts/write`+KV | DOC-ONLY |
| 4 | Data-plane Users/Permissions **resource-token** persistence + **survives key rotation** | master key (data-plane) | **WORKS** — lab-verified 2026-09-25; tokens survive primary+secondary rotation |
| 5 | Throughput cost-DoS | `databaseAccounts/.../throughputSettings/write` | DOC-ONLY |
| 6 | `sqlRoleAssignments` native-RBAC self-grant | `sqlRoleDefinitions/write`+`read` **and** `sqlRoleAssignments/write`+`read` | **WORKS** — lab-verified 2026-09-24 |

**Note (CORRECTED via lab test #3, 2026-09-24):** the native-RBAC **grant itself IS logged** — creating
a `sqlRoleAssignment` emits `Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments/write` (Started +
Accepted, with `caller`) in the Activity Log ~2-3 min later. The real blind spot is twofold: (1) it is
**NOT** `Microsoft.Authorization/roleAssignments/write`, so a SOC rule watching Azure RBAC assignments
misses it entirely; (2) the resulting **data-plane document access** (via the native-RBAC token, master
key or connection string) is not in the Activity Log — only in `DataPlaneRequests` diagnostics (off by
default), with no per-principal attribution for key/connection-string access. The wiki page
(`az-cosmosDB-privesc.md` lines 67-72) already states this precisely; no wiki change needed.

**Lab record (test #3):** RG `htrc-cosmosrbac`, serverless account `htrccosmos21640`. Created a
`sqlRoleAssignment` binding built-in *Cosmos DB Data Contributor* (`00000000-...-002`) to the operating
SP at scope `/` (account-wide) with NO `Microsoft.Authorization` change. Confirmed the
`sqlRoleAssignments/write` event appeared in Activity Log. **Teardown:** `az group delete htrc-cosmosrbac`.

**Lab record (test #6, 2026-09-25 — resource-token vs key rotation):** RG `htrc-cosmostok`, serverless
account `htrctok26398`. Minted a `Read`-scoped resource token (`user=attacker`, `permission=readperm`,
resource `dbs/tokdb/colls/tokcoll`) under the **primary** master key via the `azure-cosmos` SDK; baseline
read of the seeded item returned `top-secret-value`. Then regenerated the **secondary** key (token still
read OK) and the **primary** key (token still read OK, immediately). Rotated **primary two more times**;
the listed primary value changed on each rotation (proving rotation lands) and a corrupted key was
rejected (control) — yet the **original** resource token kept reading after 3× primary + 1× secondary
rotation. **Finding:** master-key rotation does **not** invalidate outstanding resource tokens; they
persist to their TTL (default 1h, max 5h). This **corrects** the wiki's prior remediation note that
claimed rotating keys invalidates minted tokens. Wiki updated (`az-cosmosDB-post-exploitation.md`,
resource-token section: added lab-verified WARNING + Stealth:high + corrected Hunt line — real eviction =
delete the `user`/`permission`). **Teardown:** `az group delete htrc-cosmostok` (issued --no-wait).
