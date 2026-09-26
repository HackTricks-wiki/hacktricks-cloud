# AI Foundry / Azure OpenAI / Cognitive — Candidate Attacks (not yet lab-fired)

Cost note: base Cognitive account is free; token/inference usage bills per-call — keep test calls tiny.

- [ ] Live-fire static-key replay: create a Cognitive account, retrieve key1, replay from an unauthenticated
      context (no Azure session) to confirm the leaked-key initial-entry story + which calls it authorizes.
- [ ] Confirm `raiPolicies/write` actually disables content filters on a deployment (min perms + log).
- [ ] Test OpenAI `assistants` cross-principal thread/file disclosure (UNVERIFIED) if quota allows a
      cheap deployment.
- [ ] Verify the exact semantics and security boundary of
      `AIServices/agents/endpoints/UserIdentityImpersonation/action`; the operation name alone is not
      evidence that it grants a usable impersonated identity. Keep it out of the book until reproduced.
- [ ] Reproduce `AIServices/agents/write` against an agent used by a second principal. Establish which
      definition fields can be changed, whether another caller observes them, reachable tool/resource
      impact, and the exact data-plane diagnostic footprint.
