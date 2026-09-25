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
rotation. **Then (RG `htrc-costok2`, account `htrctok212432`) extended the test to the other two
containment actions:** deleted the token's `permission` resource → token **still read for >10 min** of
continuous 20s-interval polling; deleted the `user` resource → token **still read** immediately after.
**Finding (stronger than first thought):** an outstanding resource token is **effectively irrevocable
until its TTL** (default 1h, max 5h) — NONE of {rotate both master keys, delete the permission, delete the
user} promptly evicts it; the gateway honours the issued token for its lifetime. The only reliable
in-window containment is taking the data plane offline (CMK-revoke blocked state / delete account) or
waiting out the TTL. This **corrects** the wiki's prior remediation note (rotate keys) AND my own first
correction (delete permission/user). Wiki updated (`az-cosmosDB-post-exploitation.md` resource-token
section: WARNING enumerates all three ineffective actions + Stealth:high + corrected Hunt + "mint short
TTL" prevention). **TTL-expiry poller result:** the token read OK through age 3862s and **failed at
age 3923s** with `403 (Forbidden) The authorization token is not valid at the current time` — the error
named `token start time` and `token expiry time` exactly **1h apart** (default TTL). So it dies precisely
on its TTL clock, not on any revocation; the ~5min beyond nominal 3600s is Cosmos's clock-skew grace.
**Teardown:** `az group delete htrc-cosmostok` and `htrc-costok2` both issued (--no-wait); no Cosmos
residue.
