# Managed Microsoft AD post-exploitation audit

## 2026-09-28 - documentation, CLI, schema, role, and taxonomy review

No domain, trust, authorized network, certificate, schema, password, IAM policy, or cloud resource
was created or changed. The review used current official Managed Microsoft AD documentation, the
generated audit-method table, local Google Cloud CLI 586.0.0 help, and live predefined-role metadata.
No cleanup was required.

### Retained technique

- **Delegated-administrator password reset:** retained because
  `managedidentities.domains.resetpassword` returns a new plaintext credential. Its impact is
  explicitly bounded to the delegated administrator's documented rights in the customer `Cloud`
  OU and managed groups. The account is not Domain Admin, Enterprise Admin, or built-in
  Administrator. Using it also needs a domain-joined Windows access path and network reachability.

### Removed or corrected claims

- Corrected the permission from the nonexistent
  `managedidentities.domains.resetadminpassword` spelling to
  `managedidentities.domains.resetpassword`.
- Removed “full Active Directory takeover” and automatic trusting-forest takeover. The delegated
  account cannot perform Google-reserved forest-wide operations or directory replication.
- Adding an authorized network is reachability/configuration, not a credential or standalone
  compromise.
- `managedidentities.domains.attachTrust` requires reciprocal trust configuration, DNS/network
  connectivity, a shared secret, and separate authorization of trusted identities to useful
  resources. Creating the GCP-side trust alone does not grant useful access, so it was not retained
  as a standalone technique.
- Updating LDAPS with an attacker-held certificate does not itself create a man-in-the-middle
  position: clients must trust the issuer and the attacker still needs traffic/DNS/network control.
  Clearing the certificate is disruptive-only.
- Schema extension is irreversible but the prior text identified no concrete access, secret, or
  execution outcome; it is persistence/tamper rather than useful post-exploitation.
- Domain `SetIamPolicy` is generic resource-IAM persistence. Contrary to the old prose,
  `roles/managedidentities.domainAdmin` does not contain
  `managedidentities.domains.setIamPolicy`; `roles/managedidentities.admin` does.

### Telemetry corrections

- `google.cloud.managedidentities.v1.ManagedIdentitiesService.ResetAdminPassword` is a non-LRO
  Admin Activity `ADMIN_WRITE` event and is logged by default.
- `GetDomain` is Data Access `ADMIN_READ` and is off by default.
- Subsequent Windows logon, account-management, and directory-service events are exported only when
  the domain's separate Managed Microsoft AD audit-log collection is enabled. They are not Cloud
  Audit Logs for the reset API call.

### Local verification

- Confirmed `gcloud active-directory domains reset-admin-password DOMAIN --project=PROJECT` and
  `domains describe` syntax.
- Confirmed current `roles/managedidentities.admin`, `roles/managedidentities.domainAdmin`, and
  basic Editor permissions with `gcloud iam roles describe`.
