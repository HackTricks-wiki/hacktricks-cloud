# AI Foundry / Azure OpenAI / Cognitive — Tests Done

Wiki: `az-ai-foundry-privesc.md` (refs [43]-[50]).

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `accounts/deployments/write` cost + inference-surface abuse | that action | DOC-ONLY |
| 2 | `raiPolicies/write` disable content-filters + prompt-shields | that action | DOC-ONLY |
| 3 | `accounts/write` config-tamper / UAMI / re-enable-auth | that action | DOC-ONLY |
| 4 | OpenAI `fine-tunes/write` model-backdoor | that action | **UNVERIFIED** |
| 5 | OpenAI `assistants/*` cross-principal disclosure + RAG-poison | those actions | **UNVERIFIED** |
| 6 | AIServices `agents/write` + `UserIdentityImpersonation` | those actions | **UNVERIFIED** |
| 7 | `defenderForAISettings/write` detection-evasion | that action | DOC-ONLY |
| 8 | Static-key replay (unauth, leaked key) | none | DOC-ONLY (unauth page) |
