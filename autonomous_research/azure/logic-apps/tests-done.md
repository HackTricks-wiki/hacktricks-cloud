# Logic Apps — Tests Done

Wiki: `az-logic-apps-privesc.md`, unauth `az-logic-apps-unauth`.

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | Consumption Request-trigger callback URL invoked with pure `curl`, **no Azure token** → HTTP 200, workflow runs | none (unauth, holds callback URL) | **WORKS** | Verified. Tampered `sig` → HTTP 401: the SAS `sig` is the sole auth. On unauth page. |
| 2 | `connections/listConnectionKeys/action` — steal consented-connection runtime connectionKey | that action | **WORKS (partial)** | Verified: `validityTimeSpan` is a **.NET timespan** not ISO8601; shared-key connector → `OperationNotAllowed`, so this applies to **OAuth** connectors. On privesc page. |
| 3 | Standard: `sites/host/listkeys` + `hostruntime/.../listCallbackUrl` token-less anonymous invoke | those actions | **DOC-ONLY** | Distinct from Kudu; catalog-confirmed. |
| 4 | `workflows/listSwagger` post-ex recon | `workflows/read`+listSwagger | **DOC-ONLY** | On post section. |
| 5 | Standard host env-var RCE toolbox (shares App Service host) | `Microsoft.Web/sites/config/write` | **DOC-ONLY** | Consumption does NOT share it. App Service quota=0 wall. |
| 6 | Captured callback URL survival vs disable/enable + `regenerateAccessKey` (revocation levers) | `triggers/listCallbackUrl/action` to capture; defender needs `regenerateAccessKey`/`workflows/write` | **WORKS — lab-verified 2026-09-25** | Disable/enable does NOT revoke (survives IR reflex); single-key regen insufficient in-window; rotating BOTH keys revokes but only after ~12–15 min lag. On persistence page. |

**Lab record (test, 2026-09-25 — callback URL revocation levers):** RG `htrc-lacb`, Consumption workflow
`htwf` with an HTTP `Request` trigger → `Response 200 HT-CALLBACK-OK`. `listCallbackUrl` returns a SAS URL
(`sp=/triggers/manual/run&sv=1.0&sig=<HMAC>`); baseline `curl` POST (no token) → **200**.
**(1) Disable/enable:** while disabled the trigger rejects with **HTTP 400 `WorkflowTriggerIsNotEnabled`**;
after re-enable the **same captured URL → 200 again** (disable/enable does NOT rotate the signing key — it
only blocks execution while disabled). **(2) Key regen:** `POST .../regenerateAccessKey {"keyType":"Primary"}`
left the captured URL working (200) through +40s; a freshly listed URL had a **different `sig`** but old still
valid. `keyType` accepts only `Primary`/`Secondary` (no `NotSpecified`). After rotating **both** keys, a
background poller found the old URL kept returning 200 for **~12–15 min** (03:42→03:53) then abruptly
**HTTP 401 `AuthorizationFailed`** (03:54). So key rotation is the real kill switch for a leaked URL but has a
multi-minute propagation lag; immediate stop = keep it disabled or delete the trigger/workflow.
**Teardown:** `az group delete htrc-lacb`.

**Teardown:** test RG `htrck-unauth-la` deleted; `htrc-rg4` (blob connection test) deleted; `htrc-lacb` deleted. No residue.
