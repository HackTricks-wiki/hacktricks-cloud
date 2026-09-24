# AI Foundry / Azure OpenAI / Cognitive — Candidate Attacks (not yet lab-fired)

Cost note: base Cognitive account is free; token/inference usage bills per-call — keep test calls tiny.

- [ ] Live-fire static-key replay: create a Cognitive account, retrieve key1, replay from an unauthenticated
      context (no Azure session) to confirm the leaked-key initial-entry story + which calls it authorizes.
- [ ] Confirm `raiPolicies/write` actually disables content filters on a deployment (min perms + log).
- [ ] Test OpenAI `assistants` cross-principal thread/file disclosure (UNVERIFIED) if quota allows a
      cheap deployment.
- [ ] Verify `agents/write` + UserIdentityImpersonation grants a usable impersonated identity (UNVERIFIED).
