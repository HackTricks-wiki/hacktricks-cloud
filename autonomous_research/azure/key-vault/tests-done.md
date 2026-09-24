# Key Vault — Tests Done

Lab: `azure-labs-owCfs7hi`. Wiki pages: `az-key-vault-privesc.md`, `az-keyvault-post-exploitation.md`,
`az-keyvault-persistence.md`, unauth `az-keyvault-unauth`.

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | Unauth GET on `https://<name>.vault.azure.net` → 401 + `WWW-Authenticate` header leaks **tenant ID** + resource URI | none (unauth) | **WORKS** | Verified: bogus name → NXDOMAIN; real vault resolves (CNAME → vaultcore) and returns the Bearer authority. Tenant-ID disclosure oracle. On unauth page. |
| 2 | `enableRbacAuthorization` toggle (flip access model to gain data-plane) | `Microsoft.KeyVault/vaults/write` | **DOC-ONLY** | Control-plane op catalog-confirmed (isDataAction=false); logged in Activity Log. |
| 3 | Private-endpoint approval to expose/reach a restricted vault | `.../privateEndpointConnections/write` | **DOC-ONLY** | Catalog-confirmed. |
| 4 | `keys/unwrapKey` data-plane crypto abuse | KV data-plane Crypto User | **DOC-ONLY** | Data-plane; not in Activity Log (diag off by default). |
| 5 | Whole-vault purge (destroy soft-deleted secrets/keys) | `vaults/purge` or KV role | **DOC-ONLY** | Blocked in lab where purge-protection is on. |
| 6 | `diagnosticSettings` removal to blind KV logging | `.../diagnosticSettings/write\|delete` | **DOC-ONLY** | Anti-forensics; catalog-confirmed. |
| 7 | Planted key material / cert app-cred persistence | KV data-plane write | **DOC-ONLY** | On persistence page with Stealth. |
| 8 | `createMode=recover` vault-squat persistence | `vaults/write` | **DOC-ONLY** | On persistence page. |

**Teardown:** test vault `htrckv9118` is soft-deleted with **purge protection** → cannot be manually
purged (`az keyvault purge` → `MethodNotAllowed`); Azure auto-purges **2026-09-30**. No billable resource.
