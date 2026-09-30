# Aurora DSQL research checklist

- [x] `DbConnect` / `DbConnectAdmin` action-to-database-role binding.
- [x] Authentication-token cluster/host and Region binding across two clusters.
- [x] Exact cluster-ARN IAM scope and IAM-to-database-role mapping enforcement.
- [x] Token signature, action, host, security-token, duplicate-parameter, replay, and expiry behavior.
- [x] Mapping and IAM-policy revocation against a still-unexpired token.

Details: `token-binding-2026-09-26.md`.

Future candidates:

- [ ] Underlying assumed-role session expires before a longer-lived DSQL token.
- [ ] Cross-account resource-policy token binding with a second explicitly authorized account.
- [ ] Multi-Region peer/witness endpoint binding and failover token replay.
- [ ] Active-session behavior across mapping/IAM revocation (documented to persist up to one hour).
