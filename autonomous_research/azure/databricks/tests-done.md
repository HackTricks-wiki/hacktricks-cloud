# Databricks — Tests Done

Wiki: `az-databricks-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Init-script / notebook RCE → workspace MSI | workspace access | DOC-ONLY |
| 2 | Global init scripts (fleet persistence) | admin | DOC-ONLY |
| 3 | PAT minting | workspace access | DOC-ONLY |
| 4 | Secret-scope theft (incl. KV-backed) | workspace access | DOC-ONLY |
| 5 | Unity Catalog abuse | metastore admin | DOC-ONLY |
| 6 | `accessConnectors/write` | that action | DOC-ONLY |
| 7 | `updateDenyAssignment` | that action | **UNVERIFIED** |
