# Azure Container Registry — Tests Done

Wiki: ACR privesc/post-exploitation page (refs [1]-[26]).

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | `webhooks/write` outbound exfil (distinct from getCallbackConfig read) | `registries/webhooks/write` | **REFUTED (constraint)** | LAB: ACR rejects non-routable webhook URI → `InvalidServiceUri`. Needs a reachable attacker URL. |
| 2 | `cacheRules/write`+`credentialSets/write` cache-redirect supply-chain | those actions | **REFUTED (mitigated)** | LAB: `EnforceCacheRuleAuthentication` now mandatory. |
| 3 | `registries/write` publicNetworkAccess / networkRuleSet exposure + lockout | `registries/write` | **WORKS** | LAB: public toggle writable. |
| 4 | listCredentials / regenerateCredential / generateCredentials token backdoor | those actions | **DOC-ONLY** | Heavily covered pre-audit. |
| 5 | CMK revocation DoS | `registries/write`+KV | **DOC-ONLY** | |
| 6 | **Repository-scoped token persistence/eviction matrix** — independence from Entra RBAC + admin account; which lever actually evicts | `registries/tokens/write`+`scopeMaps/write` (create) or `generateCredentials/action` (takeover) | **WORKS/CONFIRMED — lab-verified 2026-09-25 (Premium)** |

**Lab record (test, 2026-09-25 — ACR scoped-token persistence/eviction):** RG `htrc-acrtok`, Premium registry
`htrcacr14684`. Created scope map `htscope` (`content/read content/write metadata/read` on repo `app/backend`)
+ token `httoken` (password ~84 chars). Auth proven by exchanging `httoken:<pw>` at
`https://<reg>.azurecr.io/oauth2/token?service=<reg>&scope=repository:app/backend:pull` → `200` (pure HTTP
Basic, NO Azure AD token; the `/v2/` root returns 401 by design — Docker v2 auth flows through the token
endpoint). Propagation-aware matrix (ACR data-plane lags: use ≥60s waiters, my first 6s probes gave false
negatives):
- `az acr credential renew` (rotate **admin** password) → token still `200` (independent of admin creds).
- `az acr update --admin-enabled false` (disable admin user) → token still `200` (not the admin account).
- `az acr token update --status disabled` → `200`→`401` in **~9s**; re-enable → `200` in ~1s.
- `az acr token credential generate` (rotate token's own pw) → OLD pw dead immediately, NEW pw valid after
  **~51s** (brief availability gap in between).
So a scoped token is independent of BOTH Entra RBAC and the admin account; real eviction = disable/delete the
token or scope map, or regenerate its password — NOT admin-cred rotation / RBAC removal. The ARM-revocation
persistence angle was already on the wiki (line ~145); the **admin-account independence + eviction matrix**
is additive. Wiki updated (`az-container-registry-privesc.md`: WARNING with the lab-verified matrix after the
`generateCredentials` section). **Teardown:** `az group delete htrc-acrtok`.

**Teardown:** `htrc-rg3` / `htrcacr4218` deleted; `htrc-acrtok` deleted. No residue.
