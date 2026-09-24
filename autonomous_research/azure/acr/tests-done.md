# Azure Container Registry — Tests Done

Wiki: ACR privesc/post-exploitation page (refs [1]-[26]).

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | `webhooks/write` outbound exfil (distinct from getCallbackConfig read) | `registries/webhooks/write` | **REFUTED (constraint)** | LAB: ACR rejects non-routable webhook URI → `InvalidServiceUri`. Needs a reachable attacker URL. |
| 2 | `cacheRules/write`+`credentialSets/write` cache-redirect supply-chain | those actions | **REFUTED (mitigated)** | LAB: `EnforceCacheRuleAuthentication` now mandatory. |
| 3 | `registries/write` publicNetworkAccess / networkRuleSet exposure + lockout | `registries/write` | **WORKS** | LAB: public toggle writable. |
| 4 | listCredentials / regenerateCredential / generateCredentials token backdoor | those actions | **DOC-ONLY** | Heavily covered pre-audit. |
| 5 | CMK revocation DoS | `registries/write`+KV | **DOC-ONLY** | |

**Teardown:** `htrc-rg3` / `htrcacr4218` deleted. No residue.
