# Database Migration Service — assessed

## 2026-09-26 — migration-job boundary correction
- Reviewed the [migration-job API guide](https://docs.cloud.google.com/database-migration/docs/postgres/api-migration-jobs), [quick-start prerequisites](https://docs.cloud.google.com/database-migration/docs/postgres/quick-start-migrations-guide), and the current gcloud job-create reference. A DMS job needs a usable source connection profile (with valid DB credentials or configured IAM DB authentication), supported destination, and relevant destination/network authorization. `datamigration.*` alone does not supply an unknown source database password. The earlier book text incorrectly treated any project Editor as guaranteed to exfiltrate any victim DB, and treated `--dump-path` as an exfil target; corrected both.
- Removed a duplicate service-agent section that inferred arbitrary Cloud SQL/AlloyDB `executeSql`, import, and delete caller paths solely from the agent's broad role. The agent role describes what DMS can do internally; it does not establish a caller-controlled API for every permission. The valid managed migration path remains described with its prerequisites.
- No migration job, profile, database, or network resource was launched for this documentation review.

## 2026-09-28 — full privilege-escalation audit

- Reviewed the current v1 REST authorization contracts, resource schemas, audit catalog, predefined IAM roles, and stable local `gcloud database-migration` help. No cloud API mutations were performed.
- **No documented, high-value DMS-specific privilege escalation was retained.** This audit supersedes the earlier ledger wording that left a “valid managed migration path” on the privilege-escalation page: the public page now explains the caller/service-agent/database-identity boundary instead of presenting ordinary migration capabilities as escalation.
- Investigated `connection-profiles create cloudsql` as the strongest lead. Stable `gcloud` sends one DMS `CreateConnectionProfile` request containing `CloudSqlSettings`; the caller chooses the root/postgres password, ingress settings, flags, and tier, and DMS creates a Cloud SQL replica. The REST method page lists only `datamigration.connectionprofiles.create`, while the service-agent role contains `cloudsql.instances.create`.
- This is **not publishable as privesc from documentation alone**: Google's current PostgreSQL DMS
  API guide names Cloud SQL Admin for Cloud SQL profiles and jobs, and the current quick-start guide
  explicitly requires both Database Migration Admin and Cloud SQL Admin for that workflow. That
  conflicts with the narrow permission list on the generic REST method page and may reflect a
  runtime/downstream check or a broader workflow requirement. A custom-role live test is required
  before claiming the Cloud SQL permission can be omitted.
- Confirmed that `CreateConnectionProfile`, `CreateMigrationJob`, `StartMigrationJob`, and `PromoteMigrationJob` are exact v1 `ADMIN_WRITE` Admin Activity methods and long-running operations; `google.longrunning.Operations.GetOperation` and resource gets are `ADMIN_READ` Data Access. These details remain useful for a future validated technique.
- Rejected or reclassified:
  - resource `setIamPolicy` self-grant to viewer: generic IAM mutation and metadata-only because profile passwords are input-only;
  - migration-job data copy: expected migration/post-exploitation behavior requiring a usable source profile and documented destination permissions, not a proven stronger identity;
  - `migrationJobs.fetchSourceObjects`: reconnaissance on an existing job; its v1 permission is `ADMIN_READ` Data Access rather than the former `DATA_READ` claim;
  - `privateConnections.create`: a DMS connectivity primitive, not caller network membership or direct database access;
  - conversion-workspace “arbitrary DDL injection”: not supported by the official mapping-rule contract;
  - generic service-agent `executeSql`/import/delete claims: no caller-controlled DMS method was established.
- Cloud SQL/AlloyDB resources are billable and durable. No live validation was justified without a prepared disposable source and explicit cost/cleanup plan.

## 2026-09-28 — independent cross-review

- Re-opened the current v1 create/resource schemas, PostgreSQL API and quick-start guides, DMS role
  catalog, audit catalog, and stable local Google Cloud SDK 586.0.0 implementation. No cloud API was
  called and no resource was created.
- **The zero-retained-H3 conclusion stands.** No documented DMS permission was shown to cross an IAM,
  service-account, network-membership, or database-identity boundary without independent authority.
- Refined the Cloud SQL conflict rather than resolving it in either direction. The generic
  `projects.locations.connectionProfiles.create` reference lists only
  `datamigration.connectionprofiles.create`. The request schema accepts immutable
  `CloudSqlSettings`, including an input-only `rootPassword`, and the stable gcloud command constructs
  one DMS `CreateConnectionProfile` request rather than invoking the Cloud SQL API client-side.
- Conversely, the PostgreSQL API guide names Cloud SQL Admin for Cloud SQL connection profiles and
  migration jobs. The current PostgreSQL quick-start guide is even more explicit: it directs the
  migration user to hold both `roles/datamigration.admin` and `roles/cloudsql.admin` and lists
  `cloudsql.instances.create`, update, delete, connect, executeSql, import/export, login, operation,
  and user permissions. The quick-start path is broader than the generic legacy create method, so it
  does not establish the exact runtime check on that endpoint; it does establish that DMS-only
  provisioning cannot responsibly be claimed from the REST table alone.
- Reconfirmed the secret boundary: source passwords, TLS client private keys, and the Cloud SQL root
  password are input-only; read responses expose state indicators such as `passwordSet` or
  `rootPasswordSet`, not the stored values.
- Reconfirmed telemetry relevant to any future test. The exact v1 create method is
  `google.cloud.clouddms.v1.DataMigrationService.CreateConnectionProfile`, an `ADMIN_WRITE` Admin
  Activity LRO. The audit catalog classifies `FetchSourceObjects` as an `ADMIN_READ` Data Access LRO
  but also includes the exact v1 RPC in its “methods that don't produce audit logs” list; it should
  therefore not be presented as an observable Data Access event. Operation polling is Data Access
  and should not be confused with the mutation record.
- No public-page technique was added. Only the wording and primary citation for the unresolved Cloud
  SQL permission conflict needed correction.
- The coordinating lab check found `datamigration.googleapis.com` disabled and no DMS service-agent
  identity or IAM binding. Enabling the API could create a Google-managed identity whose complete
  removal is not guaranteed, so the current project was deliberately left untouched. A runtime test
  should use a disposable project where whole-project deletion is an acceptable cleanup boundary.
