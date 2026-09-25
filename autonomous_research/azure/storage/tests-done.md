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
