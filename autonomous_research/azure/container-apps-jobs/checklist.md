# Container Apps / Jobs — Candidate Attacks (not yet lab-fired)

- [ ] Retry `Microsoft.App/jobs/start/action` execution-template override after managed-environment
      provisioning is healthy. Create a manual Job with one fake secret and a canary Reader-scoped
      identity; prove secretRef access and a harmless identity-backed read without `jobs/write` or
      `listSecrets/action`, then capture propagation and Activity Log details.
- [ ] Test whether removing the job's identity or its target RBAC role immediately evicts a running/new
      overridden execution, distinguishing ordinary token-cache lifetime from a stale-authorization bug.
- [ ] Test Key Vault-backed Container Apps secret materialization after secret disable/delete, identity
      detach, and RBAC removal. Continued resolution beyond normal refresh/token lifetime is a private-
      report candidate; cached values within documented behavior are an incident-response nuance.
