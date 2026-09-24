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

**SFTP `localUsers` note** already covered.
