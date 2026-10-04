# Cloud KMS — tested and reviewed

## 2026-09-29 — external-key version migration authorization boundary

- Mapped the September 23 Preview ability to PATCH an existing `EXTERNAL`/`EXTERNAL_VPC` version's protection level and `externalProtectionLevelOptions`. This creates a per-version route override distinct from editing the shared `EkmConnection`: `externalKeyUri`, `ekmConnectionKeyPath`, and `ekmConnectionBackendOverride` can move while the version resource name remains stable.
- Resolved a current official-documentation conflict with a minimum-permission live probe. The migration guide says `cloudkms.cryptoKeys.update`; the audit catalog says `cloudkms.cryptoKeyVersions.update`. A disposable principal holding only the version permission passed authorization and received `NOT_FOUND` for an intentionally nonexistent version. A second principal holding only the key permission was denied explicitly on `cloudkms.cryptoKeyVersions.update`.
- Both calls emitted `UpdateCryptoKeyVersion` Admin Activity entries. The version-only entry showed the permission granted and status code 5 (`NOT_FOUND`); the key-only entry showed it denied and status code 7. No key, key ring, version, EKM connection, or external request was created.
- Classified the expected attack as a targeted external-key route override: a compatible attacker-controlled route that proxies/serves the same material can intercept the selected version's external crypto exchange; a wrong/invalid route produces targeted DoS. It is not a way to convert SOFTWARE/HSM keys, recover original external material, or use an arbitrary SSRF URL.
- Cleanup removed both project bindings, service accounts and active custom roles, returned Cloud KMS to its disabled baseline, and securely shredded generated keys/configs. IAM Credentials remained enabled at baseline. Exact `ht-kms-none` asset search was empty; older September 22 `ht-kms-key*` resources already in `DESTROY_SCHEDULED` were left untouched.

## 2026-09-26 — audit visibility and Autokey prerequisite review

- Reconciled five privilege-escalation and nine post-exploitation headings against the current Cloud KMS audit-method reference. Crypto-use methods (`Decrypt`, `Encrypt`, `AsymmetricSign`, `MacSign`, `AsymmetricVerify`, `MacVerify`, and `Decapsulate`) are Data Access (`DATA_READ`) and off by default; key/config lifecycle writes are Admin Activity and always on.
- Added an explicit stealth rating to every retained KMS privesc and post-exploitation technique, accounting for persistent state, request-body visibility, cross-scope attribution, and downstream operational signals rather than audit class alone.
- Corrected the Autokey repoint prerequisite: `UpdateAutokeyConfig` requires both `cloudkms.autokeyConfigs.update` on the parent folder/project and `cloudkms.cryptoKeys.setIamPolicy` on the proposed key project. An attacker-owned destination supplies the latter; the folder permission alone cannot repoint Autokey at an arbitrary victim-owned project.
- Documentation review only. No GCP resource was created or mutated.
