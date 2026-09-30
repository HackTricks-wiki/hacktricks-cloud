# Cloud KMS — research checklist

- [x] Classify per-technique stealth against the current KMS audit-method reference.
- [x] Recheck the Autokey `UpdateAutokeyConfig` cross-project authorization prerequisites.
- [x] Resolve the external-key migration guide's `cryptoKeys.update` claim against the live
      `CryptoKeyVersions.patch` authorization gate; the service enforces
      `cloudkms.cryptoKeyVersions.update`.
- [x] Add per-version EKM route fields to enumeration and document the targeted override with
      bounded MITM-versus-DoS impact and exact Admin Activity detection.
- [ ] Live-verify Autokey cross-project repointing if a disposable folder and second project become available; confirm which project/folder log scopes receive every fragment.
- [ ] Revisit new Cloud KMS HSM-management and trusted-key import/export methods for a distinct, non-duplicate attack primitive when they are generally available in the lab.
- [ ] In an existing disposable EKM fixture, change one version's URI/path/backend and immediately
      restore it. Confirm any separate `ekmConnections.use` check, successful request-body audit
      fields, same-material validation, state continuity, data-plane identity, and cross-project
      backend restrictions. Never create a permanent key/key-ring solely for this test.
- [ ] Private-first: probe API-version parity, stale-route propagation, connection/path parser
      ambiguity, and rollback behavior using only owned EKM endpoints. Treat any same-material,
      cross-project, or authorization bypass as vulnerability-report material.
