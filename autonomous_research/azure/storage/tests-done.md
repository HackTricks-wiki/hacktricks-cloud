# Storage — Tests Done

Wiki: `az-blob-storage-post-exploitation.md`, `az-storage-persistence.md`, `az-storage-tasks-post-exploitation.md`,
unauth `az-storage-unauth` (pre-existing).

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | CMK-repoint ransomware | `storageAccounts/write`+KV | DOC-ONLY |
| 2 | `encryptionScopes` lockout | `encryptionScopes/write` | DOC-ONLY |
| 3 | Disable versioning/change-feed/soft-delete (anti-forensics) | `storageAccounts/write` | DOC-ONLY |
| 4 | Account failover DoS | `storageAccounts/failover/action` | DOC-ONLY (irreversible-ish, not fired) |
| 5 | Lifecycle-to-Archive DoS | `.../managementPolicies/write` | DOC-ONLY |
| 6 | Blob inventory recon | `.../inventoryPolicies/write` | DOC-ONLY |
| 7 | Wildcard CORS exfil channel (persistence) | `storageAccounts/write` | DOC-ONLY |
| 8 | Storage Tasks fleet blob destruction/Archive/expiry (Microsoft.StorageActions) | Storage Actions Contributor + Task Assignment Contributor + Blob Data Operator | DOC-ONLY | Task Assignment Contributor does NOT include roleAssignments/write (corrected). |
| 9 | SFTP `localUsers` **survives Shared-Key-disable + key rotation** (persistence eviction-bypass) | `localUsers/write` on HNS+SFTP account | **WORKS** — lab-verified 2026-09-25 |
| 10 | SAS **revocation matrix** — which lever kills which SAS type | `generateUserDelegationKey/action` + data role (UDS); account key (svc SAS) | **WORKS/CONFIRMED** — lab-verified 2026-09-25; UDS≠service SAS revocation |
| 11 | HNS Storage ABAC Blob-vs-DFS path-condition bypass | Conditional `Storage Blob Data Reader` | **REFUTED 2026-09-26** — direct reads and scoped listings enforced the same allow/deny boundary on both endpoints |

**Lab record (test, 2026-09-25 — SFTP local-user eviction-bypass):** RG `htrc-sftp`, account
`htrcsftp26935` (StorageV2, HNS on, SFTP on). Created container `sftphome` + SFTP `localUser` `htsvc` with
an SSH public key and `permissions=rcwdl service=blob` scope. Baseline: `sftp -i key htrcsftp26935.htsvc@
htrcsftp26935.blob.core.windows.net` connected and uploaded a file. Then applied the two standard storage
containment steps: `--allow-shared-key-access false` **and** renewed **both** account keys. **Result:** the
old account key → `Authentication failure` (control confirms key path is dead), but the **SFTP local user
still logged in and uploaded a new file** (`sftp_after_hardening.txt`). What DID evict it:
`--enable-sftp false` → next login failed `Received disconnect … SSH/SFTP are not enabled for this account`
(RC 255). So neither Shared-Key-disable nor key rotation touches SFTP local users; real eviction = disable
the SFTP feature, delete the `localUser`, or delete the account. Wiki updated (`az-storage-persistence.md`
SFTP section: added lab-verified WARNING). Outbound port 22 from the harness to `*.blob.core.windows.net`
works, so SFTP data-plane tests are feasible here. **Teardown:** `az group delete htrc-sftp`.

**Lab record (test, 2026-09-25 — SAS revocation matrix):** RG `htrc-udsas`, account `htrcuds14629`, blob
`data/secret.txt`. Minted a **user-delegation SAS** (`--auth-mode login --as-user`, SP had *Storage Blob
Data Reader*) and an account-key **service SAS**; both read the blob (curl 200). Findings, all curl-verified
(the SAS request carries no identity, so this is pure bearer-token behaviour):
- **Rotate both account keys:** service SAS → `403` within ~15–30 s (control: key1 value changed);
  user-delegation SAS → **still 200** (Entra/UDK-signed, not key-signed).
- **Remove the SP's `Storage Blob Data Reader` role:** user-delegation SAS → `403` within **~20 s** — i.e.
  a UDS **is re-authorized against the delegating principal's live RBAC on every request** (opposite of the
  Cosmos resource-token behaviour, which ignored revocation until TTL).
- **`az storage account revoke-delegation-keys`:** a freshly-minted UDS → `403` within **~15 s**.
So account/service SAS is killed only by key rotation; user-delegation SAS is killed by role-removal or
`revoke-delegation-keys` but NOT by key rotation. Wiki updated (`az-storage-persistence.md` "Long-lived SAS"
section: added a lab-verified revocation-matrix WARNING + fixed the "rotate both account keys" response
line). **Teardown:** role assignment removed + `az group delete htrc-udsas`.

**Lab record (test #11, 2026-09-26 — HNS ABAC Blob/DFS differential):** Created tagged disposable
RG `htrc-abac-26926`, Standard_LRS HNS account `htrcabac26926`, filesystem `labfs`, and three fake
canaries: `allowed/canary.txt`, `denied/canary.txt`, and prefix trap `allowed-evil/trap.txt`. The caller's
management-plane Owner role had no Storage DataActions. After seeding with an account key, Shared Key
authorization was disabled and a Shared-Key control returned 403. The caller's service-principal object
ID received only `Storage Blob Data Reader`, conditioned on container `labfs` and path/prefix
`StringStartsWith 'allowed/'` for both direct read and `Blob.List` suboperation branches.

- Direct OAuth reads through `blob.core.windows.net` (`GetBlob`) and `dfs.core.windows.net` (`ReadFile`)
  were identical with API versions `2026-04-06` and `2023-11-03`: allowed returned the fake canary
  (`206` with the Range control), denied and `allowed-evil` returned 403, and an authorized missing path
  returned 404 on both.
- Scoped listing was also consistent: Blob `prefix=allowed/` and DFS `directory=allowed/` returned only
  the allowed canary; `denied/`, `allowed-evil/`, and unscoped listings returned 403. DFS
  `directory=allowed` (no trailing slash) returned 403 because it did not satisfy the literal
  `StringStartsWith 'allowed/'`; adding the slash returned 200. This is normalization/operator behavior,
  not an authorization expansion.
- `StorageBlobLogs` (explicit `StorageRead` diagnostic) recorded OAuth `GetBlob`, `ReadFile`, and
  `ListFilesystemDir`, including success/failure, requester object/tenant IDs and `AuthorizationDetails`
  with ABAC `Policy`/`NoApplicablePolicy`. These requests were absent from the Activity Log; the account,
  diagnostic-setting and role-assignment control-plane changes were logged there.
- Removing the conditional assignment left both endpoints able to read for about 90 seconds; attempt 11
  at roughly 100 seconds returned 403 on both. This was a symmetric RBAC propagation/cache window, not a
  Blob/DFS difference.

Harness lesson: `az account show --query user.name` returned the application/client ID for this service-
principal login, not the token's `oid`. Passing it to `--assignee-object-id` created a role assignment for
the wrong identifier and all positive controls stayed 403. That assignment was deleted; the corrected
assignment used JWT claim `oid=4e4b1002-38d9-4787-8c2a-321d73b3a8c0` and the allow control immediately
succeeded. Never interpret a uniform 403 matrix until the token `oid`, assignment `principalId`, and an
allowed control match.

**Teardown:** deleted the conditional role assignment first, verified the allowed Blob and DFS reads both
fell to 403, then deleted RG `htrc-abac-26926`. A final group/resource inventory confirmed that the
storage account, filesystem, diagnostic setting, Log Analytics workspace, canaries, and test role
assignments were gone.
