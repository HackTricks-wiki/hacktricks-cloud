# Cloud KMS — tested and reviewed

## 2026-09-26 — audit visibility and Autokey prerequisite review

- Reconciled five privilege-escalation and nine post-exploitation headings against the current Cloud KMS audit-method reference. Crypto-use methods (`Decrypt`, `Encrypt`, `AsymmetricSign`, `MacSign`, `AsymmetricVerify`, `MacVerify`, and `Decapsulate`) are Data Access (`DATA_READ`) and off by default; key/config lifecycle writes are Admin Activity and always on.
- Added an explicit stealth rating to every retained KMS privesc and post-exploitation technique, accounting for persistent state, request-body visibility, cross-scope attribution, and downstream operational signals rather than audit class alone.
- Corrected the Autokey repoint prerequisite: `UpdateAutokeyConfig` requires both `cloudkms.autokeyConfigs.update` on the parent folder/project and `cloudkms.cryptoKeys.setIamPolicy` on the proposed key project. An attacker-owned destination supplies the latter; the folder permission alone cannot repoint Autokey at an arbitrary victim-owned project.
- Documentation review only. No GCP resource was created or mutated.
