# Logic Apps — Tests Done

Wiki: `az-logic-apps-privesc.md`, unauth `az-logic-apps-unauth`.

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | Consumption Request-trigger callback URL invoked with pure `curl`, **no Azure token** → HTTP 200, workflow runs | none (unauth, holds callback URL) | **WORKS** | Verified. Tampered `sig` → HTTP 401: the SAS `sig` is the sole auth. On unauth page. |
| 2 | `connections/listConnectionKeys/action` — steal consented-connection runtime connectionKey | that action | **WORKS (partial)** | Verified: `validityTimeSpan` is a **.NET timespan** not ISO8601; shared-key connector → `OperationNotAllowed`, so this applies to **OAuth** connectors. On privesc page. |
| 3 | Standard: `sites/host/listkeys` + `hostruntime/.../listCallbackUrl` token-less anonymous invoke | those actions | **DOC-ONLY** | Distinct from Kudu; catalog-confirmed. |
| 4 | `workflows/listSwagger` post-ex recon | `workflows/read`+listSwagger | **DOC-ONLY** | On post section. |
| 5 | Standard host env-var RCE toolbox (shares App Service host) | `Microsoft.Web/sites/config/write` | **DOC-ONLY** | Consumption does NOT share it. App Service quota=0 wall. |

**Teardown:** test RG `htrck-unauth-la` deleted; `htrc-rg4` (blob connection test) deleted. No residue.
