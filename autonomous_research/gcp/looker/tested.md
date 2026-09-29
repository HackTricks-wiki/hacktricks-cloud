# Looker — tested research

## 2026-09-28 — privilege-escalation and post-exploitation documentation audit

No Looker instance, bucket, key, IAM policy, application identity, or other cloud resource was created or modified. Current Google Cloud primary documentation, local gcloud 586.0.0 help/source, and read-only predefined-role output were used. A read-only Service Management config lookup was rejected because the API is disabled in the test project; it did not change project state.

### Retained book techniques

- **Privilege escalation:** zero service-specific H3s. The intended project-IAM-to-Admin-via-IAM mapping is documented, but generic `resourcemanager.projects.setIamPolicy` self-grant is not duplicated as a Looker technique.
- **Post-exploitation:** one-time `looker.instances.export` to a controlled Storage destination/key; application-level modeled queries/saved-content downloads; and raw SQL Runner queries through allowed connections (three H3s).

### Material corrections

- Removed the claimed `looker.instances.update` OAuth takeover. Google OAuth users still must be provisioned through IAM, `roles/looker.admin` is what supplies Admin via IAM, and an external OAuth audience still admits only identities added through IAM.
- Corrected `--allowed-email-domains`: it is a scheduled-content/alert delivery allowlist, not a login allowlist.
- Separated Google Cloud IAM from Looker application authorization. `looker.instances.login` alone does not grant model/content/SQL Runner access. API-only Looker service accounts are the documented exception to IAM user provisioning.
- Corrected the hosted API URL from a hard-coded legacy `:19999` path to the Google-hosted port-443 `/api/4.0` path.
- Corrected SQL Runner's two-step API flow: create with `POST /sql_queries`, then execute with `POST /sql_queries/{slug}/run/{result_format}`.
- Corrected query prerequisites to application `access_data`/`explore`, saved-content permission and folder access, download caps, and SQL Runner's `use_sql_runner` dependency chain.
- Bounded SQL Runner impact by allowed connections and the connected database account. Looker does not gate SQL command type, but read-only OAuth/database identities prevent writes.
- Corrected application telemetry. The Looker audit catalog explicitly classifies API login/query/SQL Runner methods as disabled-by-default Data Access; these calls are not inherently absent from Cloud Audit Logs. Database SQL is also logged in instance logs at the default `info` threshold.
- Corrected export prerequisites to the caller's `looker.instances.export` plus the Looker service agent's documented `storage.objects.create`, bucket-policy get/set, and KMS-encrypter permissions. The stable gcloud helper returns the LRO without polling; a later status read is a separate `looker.operations.get` boundary. A CMEK-enabled instance requires its instance CMEK.
- Did not invent an audit class for `ExportInstance`: the current official Looker audited-operations table omits it. Storage/KMS downstream methods and defaults are documented exactly; the primary control-plane entry remains an explicit validation gap.

### Rejected or relocated claims

- **OAuth-client swap becomes arbitrary Looker admin:** rejected; the OAuth client is not an attacker-controlled identity provider and IAM still provisions Google OAuth users.
- **Public IP enablement grants application privileges:** rejected; it changes reachability only.
- **Read stored connection passwords/certificates:** rejected. The current `DBConnection` schema marks password, certificate, and key-file fields write-only; reads disclose metadata, not those secrets.
- **Read existing API3 client secrets:** rejected. `CredentialsApi3` returns client ID/metadata but not the secret. Creating a new credential returns a secret and is a persistence action, not sensitive-data post-exploitation.
- **Read an embed secret:** rejected as stated. Current API exposes create/delete and server-side signed-URL generation, not a general read-existing-secret primitive; edition/embedding prerequisites also apply.
- **Backup theft through `looker.backups.get/list`:** rejected. Those control-plane reads expose backup metadata; no documented backup-content download/export operation was found.
- **Scheduled export in post-exploitation:** relocated conceptually to persistence because it is a recurring configuration change. It was not duplicated here.
- **Import/delete/restart:** removed from post-exploitation as destructive-only service impact with no sensitive-information or foothold outcome.

### Official evidence used

- Looker (Google Cloud core) IAM/access-control, OAuth provisioning, user management, service-agent, import/export, logging, and audit-logging documentation.
- Stable Looker Admin REST export schema and Looker application API 4.0 login/query/SQL Runner/connection schemas.
- Looker application roles and permission-dependency documentation.
- Cloud Storage and Cloud KMS audit catalogs.
- Local `gcloud looker instances export --help`, `instances update --help`, and current predefined-role descriptions.

## 2026-09-29 — Workforce SCIM claim-source delta

- The September 2026 `enabled-for-users-groups` provider mode supersedes the prior zero-privesc
  conclusion for one identity-plane case. A compromised SCIM tenant token can patch an accepted
  workforce subject into a group, or change a mapped custom user claim, that already receives more
  privileged Looker OAuth/IAM or application-group access.
- This is documented once on the Workforce Identity Federation privilege-escalation page and linked
  from Looker. It does not make `looker.instances.update` an OAuth takeover permission and does not
  apply to arbitrary GCP services.
- No Looker or workforce resource was created. The lab identity lacks organization/workforce-pool
  access; the conclusion is bounded to Google's current SCIM, Cloud OAuth and Looker contracts.
