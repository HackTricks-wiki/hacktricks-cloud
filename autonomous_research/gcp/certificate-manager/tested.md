# Certificate Manager — tested and verified

Last checked: 2026-09-26

## Post-exploitation quality and audit review — CORRECTED

- Retained three incremental techniques: live certificate-map substitution (TLS DoS, or
  impersonation only with a separately trusted certificate), active trust-config injection for
  mTLS bypass, and Public CA EAB registration of a persistent external ACME account.
- Corrected the self-managed-certificate overclaim. Certificate Manager accepts an arbitrary
  self-signed SAN, but ordinary clients reject it; changing a certificate neither changes the
  backend nor decrypts existing forward-secret TLS sessions. A PRIMARY entry is a fallback for
  unmatched SNI, not an override for every explicit hostname.
- Removed `dnsauthorizations.create` as a standalone attack. Completing issuance also needs
  certificate creation and DNS control, the Google-managed private key is not exportable, and DNS
  write alone already lets the attacker satisfy an external ACME challenge. It adds no meaningful
  attacker capability.
- Removed the issuance-config/CA-pool bridge. Creating an issuance config does not alter existing
  certificates, and control of a private CA pool already permits certificate issuance with an
  attacker-generated key. The Certificate Manager layer adds no distinct offensive impact.
- Corrected Public CA lifecycle: an EAB secret expires unused after seven days and registers only
  one account; the resulting ACME account has no expiration. Also corrected its audit category:
  `CreateExternalAccountKey` is Data Access `DATA_WRITE`, disabled by default, not Admin Activity.
- The authorized lab has both Certificate Manager and Public CA APIs disabled. Read-only list calls
  returned `SERVICE_DISABLED`; neither API was enabled and no resources were created.

## Role surface

- `roles/certificatemanager.editor` includes create/update/use for certificates, maps, map entries,
  trust configs, DNS authorizations and issuance configs, but not their delete permissions.
- `roles/certificatemanager.owner` adds deletes.
- `roles/publicca.externalAccountKeyCreator` contains the EAB create permission plus project
  metadata reads; `roles/publicca.admin` also contains the create permission.
