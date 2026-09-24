# Glue — tested

Glue has: privesc page, post-exploitation page. No dedicated `aws-services/` enum page (organizational only).

## GetConnection plaintext-credential disclosure — VERIFIED (re-confirmation of existing page)

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1.
- **Setup:** created a JDBC Glue connection with `PASSWORD` in `ConnectionProperties`; created a
  role with an inline policy granting **only `glue:GetConnection`** (no KMS, no SecretsManager).
- **Result:** assuming that single-permission role, `aws glue get-connection` returned the
  **plaintext** `PASSWORD` + `USERNAME` + `JDBC_CONNECTION_URL`. Account default
  `ReturnConnectionPasswordEncrypted: false`; `--hide-password` (HidePassword=true) omits the
  password but the caller controls that flag so an attacker simply omits it.
- **Disposition:** NOT net-new — already documented thoroughly in
  `aws-post-exploitation/aws-glue-post-exploitation` (`## glue:GetConnection — plaintext connection
  credentials`, with min-perms confirmed, impact, logs, CloudTrail `responseElements:null` note,
  and the `PutDataCatalogEncryptionSettings` downgrade path). This test **validated the existing
  page's accuracy**. No wiki change. No duplicate created (no-garbage bar).
- **Teardown:** connection + role deleted and verified gone (EntityNotFound / NoSuchEntity).
