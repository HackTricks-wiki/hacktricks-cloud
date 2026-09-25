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
| 7 | `updateDenyAssignment` — relax managed-RG deny | that action | **REFUTED — lab-verified 2026-09-25 (Geneva-only + dataActions deny neutralises self-grant)** |

**Lab record (test #7, 2026-09-25 — updateDenyAssignment + managed-RG data self-grant):** RG `htrc-dbxdeny`,
workspace `htdbx7573` (Premium SKU — Standard is deprecated, `DatabricksStandardSkuNotSupported`), managed RG
`htdbx-managed-29916`, DBFS-root storage `dbstoragemxid5sjfb6fkw`. Two things tested and **both refute the
prior UNVERIFIED wiki claim** that `updateDenyAssignment` is an attacker unlock:

1. **`updateDenyAssignment` is Geneva-only.** `POST .../workspaces/htdbx7573/updateDenyAssignment` on api-versions
   `2024-05-01`, `2023-02-01`, `2018-04-01` all returned **`AuthorizationFailed: "This operation is only restricted
   to Geneva Action"`** (Microsoft-internal control plane). The deny assignment is `isSystemProtected:true`, so the
   generic `Microsoft.Authorization/denyAssignments/{write,delete}` cannot touch it either. **No customer path** to
   relax it.
2. **Self-granting a Storage data role is neutralised by the deny assignment's `dataActions`.** Inspected the system
   deny assignment (id `642bab85…`, name "System deny assignment created by Azure Databricks …/htdbx7573"): permission
   is `actions:['*']` **AND `dataActions:['*']`**, `notDataActions:[]` (empty), 17 `notActions`, principals `00000000…`
   (all), `excludePrincipals` = the workspace UA-MSI. Because `Microsoft.Authorization/roleAssignments/write` **is** a
   `notAction`, `az role assignment create` of `Storage Blob Data Reader` **and** `Storage Blob Data Contributor` for our
   SP (`oid 4e4b1002-…`) on `dbstoragemxid5sjfb6fkw` **SUCCEEDED**. But with those roles held, `az storage blob
   list/upload/download --auth-mode login` still returned **`AuthorizationPermissionDenied`** (waited 180s for RBAC
   propagation — not a propagation issue), and `az storage account keys list` returned **`DenyAssignmentAuthorizationFailed`**.
   The `dataActions:['*']` deny overrides any RBAC data role for every principal but the excluded UA-MSI. Only
   **control-plane `*/read`** leaks (e.g. `az storage container list` works — enumeration only, not blob contents).

**Conclusion:** the managed-RG deny assignment is a genuine security control, not a soft barrier; the real DBFS-root
data path stays the **workspace UA-MSI** (init-script → IMDS token, already documented). Wiki section rewritten from
"updateDenyAssignment — weaken the deny assignment" to "The managed-RG deny assignment (and why updateDenyAssignment is
NOT an attacker primitive)" with two WARNINGs. **Teardown:** `az group delete htrc-dbxdeny` (removes workspace +
managed RG + the two self-granted role assignments, which cannot be deleted individually — the deny blocks
`roleAssignments/delete`). Cost: Premium workspace, no cluster launched — under the $5/30min gate.
