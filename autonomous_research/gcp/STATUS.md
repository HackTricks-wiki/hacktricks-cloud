# GCP audit — status

Last updated: 2026-09-28

### 2026-09-28 — API Hub plugin boundary mapped; fixture intentionally not provisioned
- Mapped API Hub's current plugin identity chain: the hosting-service account, not the plugin-instance
  creator, is expected to receive Secret Accessor and Token Creator on referenced secrets/accounts.
  Missing caller actAs alone is therefore not a reportable boundary failure.
- Retained two sharper tests: IAM exposes `plugininstances.applyConfig` although current discovery and
  protobuf omit the corresponding RPC while update tooling accepts credential fields; and the
  2026-09-24 audit matrix omits most current plugin/instance lifecycle and execute methods. Callback
  authentication, redirect handling and cross-project target authorization are also queued.
- No API Hub instance was provisioned. The lab has both API Hub and Apigee disabled, and teardown of
  a newly provisioned API Hub leaves a seven-day soft-deleted Apigee organization/cooldown. Durable
  binary tests and cleanup gates are recorded without creating cloud residue or a public claim.

### 2026-09-28 — Storage Batch Operations execution-identity correction
- Reconciled current documentation with the existing live transform result. Real prefix transforms
  re-check caller object permissions, but bucket-list/manifest runtime failures also use the
  job-project Storage Batch Operations service agent; only project-source/CEL is explicitly described
  as processing with caller credentials. The book no longer says the service agent is uninvolved.
- Preserved the supported destructive technique and added the unverified dry-run boundary: dry runs
  return aggregate object counts and prefix-selected bytes without transforming data, but it remains
  unknown whether a caller lacking direct list/read can obtain them through service-agent access.
- No job was launched because the lab has effective Storage Intelligence edition `NONE`; activating
  its one-time 30-day trial would leave persistent entitlement/billing state contrary to mandatory
  cleanup. The exact same- and cross-project binary tests are queued for an already-enrolled fixture.

### 2026-09-28 — Audit Manager caller-write boundary securely enforced
- Live-tested project-scope `EnrollResource` with `validateOnly=true` under an isolated caller. The
  Audit Manager service agent had bucket object-create while the caller's authoritative Storage
  `testIamPermissions` result was empty. After Audit Manager IAM propagated, the request returned
  HTTP 403 naming missing caller permission `storage.buckets.getIamPolicy`.
- Granting that caller documented bucket-level Storage Admin made the identical validation return
  HTTP 200 `{}`. This rejects the same-project confused-deputy hypothesis; it is expected secure
  behavior and does not merit a HackTricks technique or vulnerability report. The strict
  folder/organization cross-project variant remains queued for a prepared hierarchical fixture.
- Admin Activity logged `AuditManager.EnrollResource` and the authorization decision, but the
  observed request body omitted both destination and `validateOnly`. All buckets, identities, keys,
  configurations, bindings, API enablement and the newly created service agent were removed.
  Authoritative live inventory is empty; Cloud Asset temporarily retains deleted-key index records.

### 2026-09-28 — CES retained-identity probe isolated to product eligibility
- Current CES discovery exposes an OpenAPI-tool partial-update hypothesis: a tool editor may be able
  to change only the schema/server while retaining service-account OAuth authentication. The test
  was designed to verify the synthetic target identity through Google `userinfo`, avoiding any
  external token receiver or raw bearer-token retention.
- The lab Owner control could not create the prerequisite application. `CreateApp` returned
  `PERMISSION_DENIED: Write access to project ... was denied`, while its Admin Activity entry showed
  `ces.apps.create` granted. This is a separate CES product-entitlement blocker, so the actAs
  boundary remains untested and no book or vulnerability claim was made.
- Cleanup removed both bounded attempts' test identities, service agent, bindings and API enablement.
  Independent IAM, Service Usage, credential and Cloud Asset checks found zero residue; no app, tool,
  receiver, token capture or billable execution existed.
- Added durable CES follow-ups plus ranked API Hub plugin, Storage Batch Operations dry-run and Audit
  Manager validate-only deputy candidates for later no-residue tests.

### 2026-09-28 — Cloud SQL login-hash export and identity-surface closure
- Live-verified Cloud SQL for SQL Server's documented `sp_help_revlogin` migration feature. After a
  no-restart flag enable, the default `sqlserver` account exported a synthetic eligible login's
  password hash and SID; the default administrator remained excluded. Disabling the flag removed
  the procedure. Added the bounded offline-cracking technique to Cloud SQL post-exploitation.
- Captured always-on `cloudsql.instances.update` start/completion records for flag transitions; the
  observed entries had null request bodies, while the direct procedure invocation produced no Cloud
  Audit Log. The page now recommends inventorying effective flags as well as alerting on updates.
- Cleanup deleted both bounded SQL Server Express fixtures, retained/final backups were absent, the
  pulled client image was removed, and the pre-existing SQL Admin API remained enabled. Authoritative
  inventory is empty; Cloud Asset Search temporarily retains one stale deleted-instance entry.
- Closed the Workbench/Colab retained-identity schedule lead: notebook execution payloads are
  unsupported for update, named-user/service-account identity gates are documented, and user ADC is
  VM-local rather than schedule state. Cloud SQL's equal-subject Workforce Identity collision is
  explicitly documented; only different-subject normalization variants remain private-first leads.
- Deterministic coverage is now 265/265 privilege-escalation, 290/290 post-exploitation and 155/155
  persistence headings with categorical Stealth; zero qualifying headings are unrated.

### 2026-09-28 — Cloud Scheduler retained-identity authorization live correction
- Live-tested a raw authenticated-job PATCH whose body contained only the job name and replacement
  URI and whose update mask was exactly `httpTarget.uri`. A separate unauthenticated canary first
  proved that `cloudscheduler.jobs.update` had propagated to the isolated caller.
- The URI-only PATCH was denied on `iam.serviceAccounts.actAs` for the retained OIDC account. After
  granting Service Account User on that account, the identical request returned HTTP 200 and
  preserved the original identity and audience. Scheduler therefore reauthorizes the retained
  account; no partial-update bypass or zero-day exists.
- Corrected the Scheduler privilege-escalation, post-exploitation and persistence pages so every
  authenticated HTTP-job update requires actAs on the configured account. `RunJob` remains a
  separate known-name primitive that does not recheck actAs.
- Deleted both jobs, both test identities, the generated key, all bindings and the isolated gcloud
  configuration. Independent verification found no active test resource, IAM reference, key,
  config or cached Scheduler credential; stale gcloud credential entries from the earlier bounded
  attempts were revoked too. The pre-existing Scheduler API and service-agent binding were preserved. Cloud Asset
  Search may retain the normal soft-deleted service-account index entry during its retention window.

### 2026-09-28 — Dialogflow live correction and new-surface refresh
- Live-tested the provisional Dialogflow configured-service-account webhook claim under an isolated
  zero-role fixture. Arbitrary external and controlled Cloud Run URLs were rejected because this
  authentication mode supports only Google APIs. A Google-API URI-only PATCH without
  `iam.serviceAccounts.actAs` was denied; the identical PATCH succeeded after granting Service
  Account User. The provisional token-capture privesc page and SUMMARY entry were therefore removed.
- Cleanup deleted the CX agent, Cloud Run control, receiver, test and service-agent identities,
  temporary key/config and every IAM binding, then returned Dialogflow to disabled. Verification
  found no active test asset, binding, local credential/config or API-state residue.
- Re-ran the complete testable-permission catalog read-only: 13,701 unique permissions and 317
  service prefixes, unchanged from the recorded baseline (8,996 GA, 4,570 Beta, 135 Deprecated;
  sorted-name SHA-256 `7c7ba6cf2827f94ac6199fd2c18125f589e655ccc7eba38e1e867a9a6d0ce9ab`).
  The latest official change-log families produced no distinct book technique.
- Fresh release/API research queued managed workload identities on load-balancer backends, Cloud SQL
  workforce-identity collisions and SQL Server login-hash export, Workbench scheduled user-ADC
  execution, Backup and DR auto-protection, and several partial-update authorization checks. These
  remain research leads until a bounded authorization or data boundary is demonstrated.
- Deterministic coverage after the correction is 265/265 privilege-escalation, 289/289 post-
  exploitation and 155/155 persistence headings with categorical Stealth: zero qualifying headings
  are unrated.

### 2026-09-28 — Final unrated sweep: delivery, SSH, backup, identity and data access
- Completed the deterministic metadata backlog across fifteen pages and retained 10 privilege-
  escalation plus 10 post-exploitation techniques. Every qualifying privesc, post-exploitation and
  persistence H3 now has categorical Stealth, with exact prerequisites, bounded impact and an
  expandable telemetry table. Each primary workstream received an independent reciprocal review.
- Compute SSH metadata now separates one-VM and inherited project-wide access and distinguishes raw
  API minima from CLI helper reads and operation waits. Filestore retains reachable-share access,
  export-rule widening and non-destructive backup cloning, with protocol-specific ports/mount syntax,
  correct zone/region flags and synchronous backup/clone sequencing. Backup and DR retains vaulted
  Compute restore and GKE Secret/PV recovery; Managed Microsoft AD is bounded to the delegated
  administrator rather than Domain or Enterprise Admin.
- Config Delivery, Firebase App Hosting, Infrastructure Manager, Service Catalog and Security
  Command Center each retain one service-specific execution or authorization boundary. Generic,
  duplicate, destructive and unsupported variants were removed. Managed Kafka retains no standalone
  privilege-escalation primitive; the generic permissions page is reduced to real resource
  `setIamPolicy` and `actAs` plus code-execution patterns.
- Dialogflow initially separated external webhook-secret recovery from a provisional configured-
  service-account token-capture claim; the subsequent live test above rejected the capture path and
  removed it. Data Fusion retains only namespace secure-store value recovery, and Workflows retains
  workflow-source/identity plus execution-data disclosure. Current audit contracts corrected older
  claims for Dialogflow, Data Fusion, Managed AD and Workflows.
- Work used current official documentation, public schemas, installed SDK/source, CLI help and
  predefined-role inspection. No cloud resource, IAM binding, service configuration or audit policy
  was mutated, so no cleanup debt exists. All targeted official links resolved. The deterministic
  scan now reports 266/266 privilege-escalation, 289/289 post-exploitation and 155/155 persistence
  headings with categorical Stealth: **zero qualifying headings remain unrated**.

### 2026-09-28 — Functions, Cloud Shell, transfer/media, VMware and network defenses
- Rebuilt ten service surfaces around 2 VMware Engine privilege-escalation and 18 post-exploitation
  techniques. Cloud Functions, Cloud Shell, Web Security Scanner, VMware Engine, Storage Transfer,
  Live Stream, Transcoder and Cloud IDS/Network Security retain consequential techniques; Dataflow
  and VPC Service Controls intentionally retain no separate post-exploitation heading after their
  duplicate or misclassified material was routed to the correct pages. Every retained heading has
  bounded prerequisites and impact, categorical Stealth and an expandable telemetry table, and all
  four workstreams received an independent reciprocal review.
- Cloud Functions now reflects the current auditable `GenerateDownloadUrl` contract and the fact
  that Cloud Functions Viewer omits `sourceCodeGet`; Cloud Shell is bounded to an already-authorized
  user session; and Web Security Scanner explicitly selects its platform and warns that active scans
  can mutate target application data. Dataflow exports remain an impact of the existing run-as-
  service-account escalation rather than a second primitive.
- VMware Engine now separates Google Cloud IAM from vCenter/NSX authority, corrects CloudOwner to
  the restricted `Cloud-Owner-Role`, and retains credential-plane crossing, resource IAM self-grant,
  VM cloning and NSX interception. Storage Transfer, Live Stream and Transcoder retain only managed-
  identity data-movement or credential/input disclosure chains with current helper, LRO and Storage
  prerequisites; destructive and duplicate variants were removed.
- Cloud IDS/Network Security retains selective IDS/NGFW/DNS suppression plus NSI in-band and out-of-
  band inspection. Exact Compute and Network Security method names, operation polling and `.use`
  boundaries were corrected. VPC-SC reads are enumeration, boundary changes are privilege
  escalation, durable rules are persistence, and underlying data reads belong to the protected
  service; dry-run violations remain Policy Denied signals even though sink routing can exclude them.
- Work used current official documentation, installed SDK/source and predefined-role inspection.
  No cloud resource, IAM binding, audit policy or service configuration was read or changed, and no
  cleanup debt exists. All targeted official links resolved. The deterministic scan now finds
  256/273 privilege-escalation, 279/304 post-exploitation and 155/155 persistence headings with
  categorical Stealth, leaving 42 qualifying headings to audit.

### 2026-09-28 — Cloud Build, Bare Metal Solution, Looker, Managed Lustre and Parallelstore
- Rebuilt five service surfaces around 3 privilege-escalation and 5 post-exploitation techniques.
  Every retained attack heading now has exact prerequisites, bounded impact, categorical Stealth
  and an expandable telemetry table; each primary audit received an independent reciprocal review.
- Cloud Build now retains stored-output recovery through Cloud Logging, customer-owned Storage or
  the Google-owned default log bucket, with the helper's preliminary `GetBuild` and the customer's
  inability to inspect Google's bucket-side audit trail made explicit. Trigger mutation remains in
  privilege escalation; standalone approval, cancellation and destructive actions were rejected.
- Bare Metal Solution now separates the standard `loginInfo`/Secret Manager initial-password path
  from the optional Preview `LoadInstanceAuthInfo`/CMEK path and keeps only consequential NFS
  allowlist expansion in post-exploitation. SSH-key registration, serial-console enablement, root-
  squash flags and snapshot restore are not presented as automatic access or privilege escalation.
- Looker now distinguishes Cloud IAM from application authorization, removes the false OAuth-client
  and allowed-email-domain takeover claims, and retains one-time instance export, modeled query/
  saved-content access and SQL Runner. Managed Lustre and Parallelstore each retain only the bounded
  Storage confused-deputy chain formed by import under a stronger transfer identity followed by
  export to an attacker-controlled bucket; cleanup requires mount-based removal of staged files.
- Work used current official documentation, public discovery schemas, local CLI/source and role
  inspection. No cloud resource, IAM binding, API state or service configuration was changed, and
  no cleanup debt exists. All 49 unique book references resolved. The deterministic scan now finds
  254/274 privilege-escalation, 263/326 post-exploitation and 155/155 persistence headings with
  categorical Stealth, leaving 83 qualifying headings to audit.

### 2026-09-28 — App Engine, API Keys, Batch, PAM, Binary Authorization, Config Controller, Cloud Domains and Service Directory
- Rebuilt eight service surfaces around 5 privilege-escalation, 13 post-exploitation, 2 enumeration
  and 2 resource-level persistence techniques. Every retained attack heading has explicit minimum
  prerequisites, bounded impact, categorical Stealth and an expandable telemetry table; the batch
  received reciprocal review across independent service groups.
- App Engine removed deletion and duplicate deployment headings, corrected Memcache Console versus
  in-app audit behavior, version-read audit classes, Logging permissions and source-retention bounds.
  `exportAppImage` remains a ledger-only candidate because destination authorization, writer identity
  and victim/destination telemetry are not yet established.
- API Keys retains only service-account-bound authorization-key escalation; ordinary key creation,
  secret reads and restriction changes are not IAM escalation. Batch retains run-as-service-account
  execution with exact reporter/logging prerequisites, and PAM retains entitlement activation while
  rejecting public requester and self-approval claims.
- Binary Authorization now requires an actual GKE/Cloud Run deployment foothold after policy,
  attestor or breakglass abuse. Config Controller is bounded to the configured KCC identity, correct
  Kubernetes audit classes and real Secret material. Cloud Domains and Service Directory split reads
  into enumeration and resource IAM into persistence, while retaining only consequential DNS,
  transfer/contact and endpoint-redirection behaviors.
- Work used current official documentation, local CLI/source/role inspection and a read-only existing
  App Engine inventory query. No cloud resource, IAM binding or service configuration was created or
  changed; the Binary Authorization source-inspection clone was removed and no cleanup debt remains.
  The deterministic scan now reports 251/284 privilege-escalation, 258/334 post-exploitation and
  155/155 persistence headings with categorical Stealth, leaving 109 qualifying headings to audit.

### 2026-09-28 — BigQuery, Compute Engine, Vertex AI and IAM end-to-end audit
- Rebuilt and independently cross-reviewed four major surfaces. Retained 12 BigQuery privilege-
  escalation, 6 post-exploitation, 4 persistence and 1 authenticated external-access techniques;
  15 Compute privilege-escalation, 23 post-exploitation and 4 persistence techniques; 12 Vertex AI
  privilege-escalation and 4 post-exploitation techniques; and 2 IAM persistence techniques. Every
  retained attack heading has bounded impact, categorical Stealth and an expandable telemetry table.
- BigQuery reciprocal review removed seven destruction, availability, anti-recovery, cost-abuse and
  ransom-only headings that did not meet the post-exploitation sensitive-information taxonomy. It
  also moved SQL injection out of enumeration, corrected authenticated broad-dataset sharing,
  bounded continuous-query regions/security features and documented the authorized-view contract
  conflict rather than choosing one contradictory official source.
- Compute reciprocal review separated unconditional project-common metadata `actAs` from raw
  per-instance metadata authorization, downgraded unclassified OS Login monitoring signals from
  “logged by default” to “verify,” fixed regional-disk IAM REST syntax, and made helper-read
  permissions explicit. Destructive-only CDN, lifecycle and anti-recovery headings remain excluded.
- Vertex AI reciprocal review split Bigtable feature fetch from deprecated Optimized embedding
  search, added reliable RAG-import LRO polling and exact cleanup, bounded dataset export to image
  datasets, corrected Agent Engine identity selection and default-service-agent Storage exposure,
  and marked audit-catalog omissions as unknown rather than proof of silence.
- IAM removed invalid self-renewal claims: current official behavior rejects self-impersonation and
  prevents self-signing output from being used against IAM, IAM Credentials or OAuth. A dedicated
  persistence page now covers hierarchy allow-policy grants and bounded service-account undelete.
  One contained undelete test was inconclusive; cleanup verified zero matching accounts, bindings,
  local keys or temporary cleanup grants.
- This batch otherwise used current official documentation, local CLI/source and predefined-role
  inspection. No test asset remains. The previous manually reported metadata-scan totals could not
  be reproduced even against their published pre-batch commit, so
  `scripts/check_gcp_technique_metadata.mjs` is now the canonical deterministic scan. It reports
  246/287 privilege-escalation, 245/344 post-exploitation and 153/153 persistence sections rated,
  leaving 140 qualifying privesc/post-exploitation sections to audit under this explicit definition.

### 2026-09-28 — Workload Identity Federation, OS Config, Contact Center Insights and AlloyDB
- Rebuilt Workload/Workforce Identity Federation and OS Config around 9 genuine privilege-
  escalation and 2 persistence primitives, and rebuilt Contact Center Insights and AlloyDB around
  9 post-exploitation and 4 AlloyDB persistence primitives. All 24 retained headings have exact
  prerequisites, bounded impact, categorical Stealth and expandable telemetry; each service
  received an independent review.
- Corrected federation provider/restoration authority, SAML key-overlap and uploaded-JWKS bounds,
  removed the false general-purpose SCIM group-injection path, and bounded managed workload
  identities to X.509/SPIFFE. Added org-scoped workforce trust while separating pool administration
  from target-resource IAM; rejected OAuth-client creation as a standalone foothold because the
  supported application-integration path additionally depends on an IAP application.
- Corrected OS Config patch artifact/VM-SA dependencies, zonal versus project policy scope,
  legacy-recipe rerun behavior, standard versus custom agent identity, and policy-orchestrator
  quota/service-agent prerequisites. The predefined `patchDeployments.execute` permission is not
  presented as usable because no current public REST or CLI method exposes it.
- Corrected Contact Center Insights signed-audio, supported-format service-agent import and
  cross-project BigQuery export boundaries. Corrected AlloyDB Viewer-level export, managed
  `alloydbsuperuser`, IAM database-role enrollment, Data API/MCP authorization, restore-source
  authorization and durable native-database/network residue.
- This batch used current official documentation, local CLI/source and predefined-role inspection,
  independent review, one read-only disabled-API state check, and 80 successful unique reference-
  link checks. It created or changed no cloud resource, IAM policy or service configuration and
  left no cleanup debt. The maintained qualifying scan now finds 232/268 privilege-escalation and
  253/352 post-exploitation sections with explicit Stealth; persistence is 151/151. This leaves 135
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Cloud Identity, Developer Connect, Advisory Notifications and Healthcare
- Rebuilt Cloud Identity, Developer Connect, Advisory Notifications and Cloud Healthcare around 3
  genuine privilege-escalation, 13 post-exploitation, 3 service-level persistence and 3
  unauthenticated/external-access primitives. All 22 retained headings have exact prerequisites,
  bounded impact, categorical Stealth and expandable telemetry; every service received independent
  reciprocal review.
- Corrected Cloud Identity group-role versus customized-settings authority, security/locked-group
  restrictions, anonymous archive versus authenticated membership visibility and Workspace/DWD
  audit attribution. Corrected Developer Connect's GA Admin versus Beta token-accessor boundary,
  named-link token scope, self-selected account-connector token, provider protections and
  conditional downstream CI/CD escalation.
- Corrected Advisory Notifications by separating optional organization-level Sensitive Actions
  delivery from mandatory notices, Essential Contacts and SCC findings. A bounded lab probe reached
  only repeated API initialization failures; no settings document was returned and no PATCH was
  sent. Both temporary API enablements were successfully disabled, final state was verified, and
  no residue remained.
- Corrected Healthcare caller-versus-P4SA authorization, FHIR/DICOM/HL7v2 read and ingest surfaces,
  import/export semantics, de-identification value bounds, consent-config restoration and future
  BigQuery/Pub/Sub delivery. The external-access page now limits `allAuthenticatedUsers` to an
  unrelated authenticated Google principal rather than tokenless `allUsers` access.
- Apart from the Advisory Notifications initialization probe, this batch made no cloud mutation.
  Current documentation, local CLI/source and predefined-role inspection, reciprocal review, and
  125 successful unique reference-link checks support the result. The maintained qualifying scan
  now finds 223/266 privilege-escalation and 244/355 post-exploitation sections with explicit
  Stealth; persistence is 150/150. This leaves 154 qualifying privesc/post-exploitation sections to
  audit.

### 2026-09-28 — BeyondCorp, BigLake, Container Analysis and VM Migration
- Rebuilt BeyondCorp, BigLake/Lakehouse, Container Analysis and VM Migration around 6 genuine
  privilege-escalation, 9 post-exploitation and 4 service-level persistence primitives. All 19
  retained headings have exact prerequisites, bounded impact, categorical Stealth and expandable
  telemetry; every service received independent reciprocal review. VM Migration intentionally
  retains no persistence heading because its old candidates were one-shot mutations, not durable
  attacker access.
- Corrected BeyondCorp's browser/web-only gateway scope, caller/delegating-service-account/end-user
  identity split, policy-version-safe IAM reads, helper preflight/poll permissions and existing-VPC
  route bound. Cross-VPC upstream replacement remains an unverified test lead rather than a claim.
  Corrected BigLake by separating BigQuery connection-backed tables, stable Lakehouse/Iceberg
  catalogs and classic regional metastore tables; fixed condition-safe resource IAM, the stable v1
  `LoadIcebergTableCredentials` RPC, SQL-DDL versus direct table-creation telemetry and credential/
  snapshot/location impact bounds.
- Corrected Container Analysis's dual occurrence/note authorization, immutable versus output-only
  fields, concurrency-safe policy restoration and multi-project Binary Authorization attestor/note
  trust edges. A stored invalid signature is not an authorization bypass. Corrected VM Migration's
  current v1/global resource paths, stale Preview-guide command examples, caller versus host P4SA
  `actAs` checks, opt-in target runtime identity and conditional downstream Compute evidence.
- This batch used current official documentation, local CLI/source and predefined-role inspection,
  reciprocal review, and 65 successful unique official-reference-link checks. It accessed or
  mutated no cloud resource, IAM policy or service configuration and left no cleanup debt. The
  reproducible scan now finds 220/267 privilege-escalation and 231/345 post-exploitation sections
  with explicit Stealth; persistence is 148/148. This leaves 161 qualifying privesc/post-
  exploitation sections to audit.

### 2026-09-28 — Analytics Hub, Certificate Authority Service, Data Fusion and Deployment Manager
- Rebuilt Analytics Hub, Certificate Authority Service, Data Fusion and Deployment Manager privilege
  escalation around 3, 3, 3 and 2 genuine primitives. Added one Deployment Manager
  post-exploitation technique and one CA Service persistence technique. All 13 retained headings
  have exact prerequisites, bounded impact, categorical Stealth and expandable telemetry; every
  service received independent review.
- Corrected Analytics Hub listing, clean-room and Pub/Sub subscription identity/cardinality bounds;
  CA raw-certificate issuance, template/pool constraints, KMS signing and subordinate-CA trust
  bounds; and Data Fusion design-time, pipeline-VM, service-agent, RBAC and namespace-IAM
  boundaries. The official Analytics Hub audit reference remains internally inconsistent about
  `SubscribeListing`, so the method-detail Data Access classification is explicitly bounded pending
  a live capture. Data Fusion namespace-IAM audit class/default/method is likewise not asserted
  without evidence.
- Corrected Deployment Manager's current deprecation dates, Google APIs Service Agent deputy model,
  raw REST versus helper permissions, cross-project service-account attachment and downstream
  logging. A synthetic deployment proved that a deployment-level
  `roles/deploymentmanager.admin` binding lets an otherwise unprivileged principal read that exact
  deployment; it does not grant project-level create. The direct policy was restored, the
  deployment, bucket and temporary service account were deleted, the initially disabled API was
  disabled again, and residue checks found no matching assets.
- No other service was accessed or mutated. Current official documentation, local CLI/source
  inspection, independent review and 60 successful unique official-reference-link checks support
  this batch. The reproducible scan now finds 214/265 privilege-escalation and 222/351
  post-exploitation sections with explicit Stealth; persistence is 155/155. This leaves 180 qualifying
  privesc/post-exploitation sections to audit.

### 2026-09-28 — Cloud Scheduler, Spanner, Cloud Source Repositories and Runtime Config
- Rebuilt Cloud Scheduler privilege escalation around 4 genuine primitives, Spanner around 3 and
  Cloud Source Repositories around 2. Replaced Runtime Config's four overbroad privilege-escalation
  claims with one config-IAM self-grant, and added dedicated post-exploitation coverage for Runtime
  Config variable recovery and private Cloud Source Repositories clone/history recovery. All 12
  retained headings have exact prerequisites, bounded impact, categorical Stealth and expandable
  telemetry; every service received independent review.
- Corrected Scheduler's OAuth/OIDC, forced-run, App Engine and Pub/Sub identity boundaries;
  Spanner's policy-helper, cross-project backup/restore, encryption, IAM/FGAC and LRO boundaries;
  and Source Repositories' trigger-pinned identity, unsupported custom-role permission, conditional
  IAM preservation and disabled-by-default Git audit methods. Removed destructive-only, duplicate
  and nonexistent export claims.
- Corrected Runtime Config's stale `getIamPolicy` failure claim and separated Deployment Manager's
  documented June 30, 2027 shutdown from the independently callable Runtime Config API. A synthetic
  config, direct config IAM binding, plaintext variable and short waiter verified the policy and
  read paths. The policy was restored, the config was deleted, list/describe confirmed absence and
  the previously enabled API was left unchanged. No matching Runtime Config audit entry was
  observed; the page bounds that result by the disabled project Data Access setting and Google's
  current omission of Runtime Config from the supported-services audit catalog.
- No other service was accessed or mutated. Official documentation, local CLI/source inspection,
  independent review and 50 successful unique official-link checks support this batch. The
  reproducible scan now finds 203/270 privilege-escalation and 221/350 post-exploitation sections
  with explicit Stealth; persistence is 155/155. This leaves 196 qualifying
  privesc/post-exploitation sections to audit.

### 2026-09-28 — Dataflow, Database Migration Service, Cloud Billing and Service Usage
- Rebuilt Dataflow privilege escalation around 2 genuine primitives and Cloud Billing around 1.
  Both pages now state exact minimum permissions, bounded impact, categorical Stealth and expandable
  telemetry. Database Migration Service and Service Usage retain zero H3 techniques because the
  reviewed operations do not yet demonstrate a distinct privilege boundary crossing.
- Corrected Dataflow artifact replacement permissions and generation semantics, inline Beam YAML
  worker execution, Flex Template launch permissions, worker/service-agent identity bounds and
  exact job telemetry. Corrected Cloud Billing's account-versus-project IAM boundary, safe versus
  raw policy replacement, two-resource project-linking authorization, payment-profile exception and
  billing-scope audit queries.
- Reclassified Service Usage enable/use/disable, legacy and Cloud Quotas writes, hierarchical
  consumer policy, deprecated MCP policy, and authorization-key behavior. Read-only live requests
  confirmed that the old MCP and content-security policies return `SU_MCP_DEPRECATED`, while the
  current consumer policy remains readable; no configuration was changed.
- DMS Cloud SQL destination-profile creation remains an unresolved authorization boundary: the
  generic REST method lists only the DMS create permission, while current workflow guidance requires
  Cloud SQL Admin. The lab has DMS disabled and no DMS service agent, so enabling it could leave a
  managed identity behind. The exact least-privilege test and output-only Cloud SQL ID cleanup plan
  are queued only for an already-enabled disposable project whose deletion is acceptable.
- This batch retained 3 techniques total, used official documentation, local CLI/source inspection,
  independent review and read-only API checks, and made no cloud mutation. The reproducible scan now
  finds 194/278 privilege-escalation and 219/348 post-exploitation sections with explicit Stealth;
  persistence is 155/155. This leaves 213 qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Bigtable, Dataplex, Apigee and Document AI
- Rebuilt Bigtable, Dataplex and Apigee privilege escalation around 5, 3 and 3 genuine primitives,
  and Document AI post-exploitation around 2. All 13 retained headings now have exact
  prerequisites, bounded impact, categorical Stealth and an expandable telemetry table; every
  service received an independent review.
- Corrected Bigtable resource-IAM scope, cross-project restore/CMEK prerequisites, helper-side LRO
  polling and authorized-view update behavior. Direct logical-view IAM remains an unproven live
  lead rather than a book claim. Corrected Dataplex task identity, backing-asset role propagation,
  policy-tag bounds and control-plane versus downstream logging.
- Corrected Apigee's author/deploy permission split, optional service-account attachment, Space and
  Archive boundaries, managed-versus-Hybrid runtime logging and condition-safe environment IAM.
  Corrected Document AI dataset extraction to the public v1beta3 surface and bounded cross-project
  processor-version imports by destination P4SA trust, schema/state/region and VPC Service Controls.
- This batch used current official documentation, local CLI/source checks and read-only predefined-
  role inspection only. It created no cloud resource, changed no IAM or service configuration and
  left no cleanup debt. The reproducible qualifying-H3 scan now finds 191/295 privilege-escalation
  and 219/348 post-exploitation sections with explicit Stealth; persistence is 155/155. This leaves
  233 qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Cloud Functions, Managed Kafka, Dataproc Metastore and Google SecOps
- Rebuilt Cloud Functions privilege escalation around 4 genuine primitives, and Managed Kafka,
  Dataproc Metastore and Google SecOps post-exploitation around 6, 4 and 6 respectively. All 20
  retained headings now have exact prerequisites, bounded impact, categorical Stealth and an
  expandable telemetry table; every service received independent cross-review.
- Corrected generation-specific Cloud Functions source-upload permissions, runtime/build identity
  boundaries, preservation-safe environment updates and v1 upload telemetry. The isolated generated
  v1 method-detail label conflicts with the official permission classification and a prior live
  capture: `GenerateUploadUrl` is retained as always-on Admin Activity.
- Corrected Managed Kafka's SASL-versus-mTLS and Kafka ACL boundaries, Connect service-agent and
  cross-project dependencies, broker-protocol telemetry, offset mutation prerequisites and Schema
  Registry deletion contract. Corrected Dataproc Metastore caller-versus-service-agent Storage
  authorization, query artifacts, named-backup topology and LRO logging.
- Corrected Google SecOps search versions and logging, rule/deployment mutation semantics, lookup-data
  poisoning, feed archival and the migrated SOAR bulk-close request/evidence contract. Unsupported
  retention and playbook claims were not retained.
- This batch used current official documentation, local CLI/source checks and independent review
  only. It created no cloud resource, changed no IAM or service configuration and left no cleanup
  debt. The reproducible qualifying-H3 scan now finds 180/302 privilege-escalation and 217/352
  post-exploitation sections with explicit Stealth; persistence is 155/155. This leaves 257
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Dataform, Network Security, reCAPTCHA Enterprise and Eventarc
- Rebuilt Dataform privilege escalation around 2 genuine primitives, Network Security around 6,
  reCAPTCHA Enterprise post-exploitation around 6, and Eventarc around 1 privilege-escalation, 4
  post-exploitation and 1 persistence primitive. All 20 retained headings have exact prerequisites,
  bounded impact, categorical Stealth and expandable telemetry; all four service audits received
  independent cross-review.
- Corrected Dataform strict-act-as behavior and rejected the stale internal scheduled-commit chain:
  `repositories.commit` is internal-repository-only, while strict mode prevents cron-scheduled
  releases for those repositories. Corrected Network Security AuthzPolicy targeting/evaluation,
  TLS `allowOpen`, address-group, intercept-deployment and resource-IAM boundaries.
- Bounded reCAPTCHA policy/IP/firewall/legacy-secret/model-feedback/related-account behavior by
  key type, tier, caller-side enforcement and current telemetry. Corrected Eventarc delivery versus
  destination-runtime identities, Advanced topology/token prerequisites, exact publishing logs and
  the one genuine recurring OAuth-token persistence chain.
- This batch used current official documentation, local CLI/source checks and read-only API-enabled
  state/predefined-role inspection only. It created no cloud resource, changed no IAM or service
  configuration and left no cleanup debt.
- The reproducible qualifying-H3 scan now finds 177/306 privilege-escalation and 201/357
  post-exploitation sections with explicit Stealth; persistence is 155/155. This leaves 285
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Cloud Deploy, Pub/Sub, Workflows and Sensitive Data Protection
- Rebuilt Cloud Deploy privilege escalation around 3 genuine primitives, Pub/Sub around 3,
  Workflows around 4 and Sensitive Data Protection post-exploitation around 5. Moved the recurring
  DLP scan into a new service-level persistence page. All 16 retained headings have exact
  prerequisites, bounded impact, categorical Stealth and expandable telemetry, and all four service
  audits received independent cross-review.
- Corrected Cloud Deploy's release/rollout and default-account `actAs` checks, current task schema,
  allow-missing PATCH authorization and caller-versus-execution-account boundaries; Pub/Sub push
  OIDC, VPC-SC, export-identity and downstream logging boundaries; and Workflows default identity,
  raw REST versus CLI permissions, call logging, callback scope and current audit methods.
- Corrected DLP's most consequential telemetry error: `CreateDlpJob`, `CreateJobTrigger` and both
  template updates are always-on Admin Activity, not silent Data Access. Bounded all scans and
  cross-project exports by service-agent IAM, removed the caller-supplied `content:inspect` non-
  technique, and split raw unwrapped-key disclosure from server-side KMS-wrapped re-identification.
- This batch used official documentation, local CLI/source checks and read-only predefined-role
  inspection only. It created no cloud resource, changed no IAM or service configuration and left
  no cleanup debt.
- The reproducible qualifying-H3 scan now finds 170/311 privilege-escalation and 193/364
  post-exploitation sections with explicit Stealth; persistence is 154/154. This leaves 312
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — App Engine, Composer, Resource Manager and Artifact Registry
- Rebuilt App Engine privilege escalation around 2 genuine primitives, Composer privilege
  escalation around 4, Resource Manager privilege escalation around 5 and Artifact Registry
  post-exploitation around 6. Every retained section has exact prerequisites, bounded impact,
  categorical Stealth and an expandable telemetry table; all four rewrites received independent
  cross-review.
- Added a missing IAM v3 expected escalation path: a caller with the project-side PolicyBinding
  permission and organization-side PAB bind/unbind permission can delete a project-principal-set
  binding or conditionally exclude a controlled principal. This restores eligibility only; an
  existing allow grant remains necessary, deny still applies and other PABs remain effective.
- Live-validated project-scoped tag telemetry with a no-condition fixture. TagValue IAM emitted
  `google.cloud.resourcemanager.v3.TagValues.SetIamPolicy` rather than the summary catalog label and
  omitted the granted member/role. TagBinding create/delete emitted paired Admin Activity entries
  for value-side and project-side authorization. The binding, value and key were deleted and direct
  tag plus Cloud Asset/IAM searches confirmed no residue.
- Corrected App Engine deployment/debug identities and log classes; Composer create/PyPI/Airflow/
  DAG-injection bounds; Resource Manager IAM/tag/move commands and authorization; and Artifact
  Registry downloads, export, public exposure, scanning/platform logging and attachment semantics.
- The reproducible qualifying-H3 scan now finds 175/341 privilege-escalation and 188/366
  post-exploitation sections with explicit Stealth; persistence remains 153/153. This leaves 344
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Storage, Artifact Registry, Bigtable and model-router boundary
- Rebuilt Cloud Storage privilege escalation around 4 genuine primitives, Artifact Registry
  privilege escalation around 3 and Bigtable post-exploitation around 5. Reciprocal cross-review
  corrected raw versus condition-safe IAM writes, HMAC constraints and metrics, Composer/Cloud
  Build telemetry, Docker probe permissions, tag and `setIamPolicy` semantics, Bigtable
  read-modify-write permissions, `DropRowRange` detection and change-stream recovery limits.
- Removed or folded low-value reads/writes, destructive-only actions, obsolete GCR coverage,
  unsupported staging races and duplicate techniques. Also corrected Artifact Registry
  `ExportArtifact` to off-default Data Access `DATA_READ`, with start/completion LRO entries when
  enabled.
- Live-tested API Gateway Preview model routing against a disposable arbitrary HTTPS backend.
  Validation accepted the backend, but the router forwarded a one-hour Google-signed identity JWT
  whose audience was exactly that backend URL—not a reusable OAuth access token. The token-leak
  hypothesis is closed; arbitrary-backend trust remains an expected high-trust configuration
  concern. The gateway and every fixture asset were deleted, the three initially disabled APIs
  were restored to disabled, and Cloud Asset/IAM searches found no residue.
- The reproducible qualifying-H3 scan now finds 165/356 privilege-escalation and 182/367
  post-exploitation sections with explicit Stealth; persistence remains 153/153. This leaves 376
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — IAM, Cloud Build, Cloud SQL, Discovery Engine and API Gateway MCP
- Rebuilt IAM privilege escalation around 7 genuine primitives, Cloud Build privilege escalation
  around 3 and Cloud SQL post-exploitation around 9. Every retained H3 has exact prerequisites,
  bounded impact, categorical Stealth and an expandable telemetry table. Reciprocal cross-review
  corrected IAM Credentials logging, current `sign-blob`, role/key/policy semantics, Cloud Build
  runtime identities and trigger/token logging, and Cloud SQL Data API, clone/restore, proxy TLS,
  replica-stop and final-backup behavior.
- Added a dedicated Discovery Engine post-exploitation technique for periodic BigQuery ingestion.
  Google documents that periodic connectors do not enforce imported source ACLs, so an authorized
  Gemini Enterprise app user can search the indexed copy without direct BigQuery data permission.
  The page bounds this to indexed/retrievable fields and the last successful one-, three- or
  five-day sync; it is not arbitrary live-table access or a BigQuery IAM bypass. The separate new
  BigQuery data-agent publication path was rejected as privilege escalation because each user must
  complete OAuth and the agent acts with that user's own permissions.
- Live-verified API Gateway's new OpenAPI 3.x MCP surface with a harmless public GET backend.
  Anonymous `initialize` and default-unprotected `tools/list` returned the exact tool name,
  description and input schema; `tools/call` correctly inherited the route's deliberately anonymous
  policy. Platform logs captured the outer `/mcp` request and
  `google.api.discovery.v1.McpDiscoveryService.ListMcpTools`. Added the useful recon technique and
  completed impact/stealth/log metadata for all three API Gateway unauthenticated H3s.
- Deleted the gateway, config and API; restored API Gateway, Service Management and Service Control
  to disabled; removed local captures; and verified Cloud Asset Inventory and project IAM contained
  no `ht-mcp-*` residue.
- The reproducible qualifying-H3 scan now finds 163/372 privilege-escalation and 180/377
  post-exploitation sections with explicit Stealth; persistence remains 153/153. This leaves 406
  qualifying privesc/post-exploitation sections to audit.

### 2026-09-28 — Firebase, Monitoring, Cloud DNS and 2026 bulletin reconciliation
- Rebuilt Firebase privilege escalation around 5 genuine paths, Cloud Monitoring post-exploitation
  around 8 and Cloud DNS post-exploitation around 7. Every retained technique has exact minimum
  prerequisites, bounded impact, categorical Stealth and an expandable telemetry table. Independent
  cross-review corrected Identity Platform/IAM signing, tenant-policy preservation, inherited audit
  settings, Monitoring helper permissions, Metrics Scope boundaries, DNS policy PATCH syntax,
  peering/forwarding prerequisites and DNSSEC timing.
- Removed or folded 35 false, duplicate, miscategorized or low-value headings across those pages.
  A reproducible scan of H3 blocks that already contain both Potential Impact and Logs generated now
  finds 132/362 privilege-escalation and 162/380 post-exploitation sections with an explicit Stealth
  rating; persistence remains 153/153. That leaves 448 qualifying privesc/post-exploitation sections
  to review.
- Reconciled the historical cross-project page with nine fixed 2026 managed-service issue families,
  including GKE Multi-Cloud target-project authorization, managed connector/runtime escapes,
  service-agent confused deputies, repository takeover and cross-tenant log disclosure. Added a
  durable variation checklist without presenting patched issues as current exploits.
- Corrected the stale treatment of GCP-2026-059 / CVE-2026-4644: unauthorized HTTP Connector
  service-account attachment was fixed on December 11, 2025 and is no longer a live book technique.
  Current connection-IAM self-grant remains privilege escalation; authorized use of stored
  connection credentials moved to a dedicated post-exploitation page. `ExecuteSqlQuery` audit
  visibility remains unknown because the current official method catalog does not list it.
- This batch used documentation and read-only inventory checks only. It created no cloud resource,
  enabled no API and changed no IAM/service configuration. A final inventory found none of the
  prior `ht-*` identities, bindings or datasets, and Data Catalog remained disabled.

### 2026-09-28 — BigQuery/Vertex AI privesc and SCC post-exploitation audit batch
- Rebuilt the BigQuery and Vertex AI privilege-escalation pages around 13 and 12 genuine paths, and
  Security Command Center post-exploitation around 9. Every retained technique now has exact minimum
  prerequisites, bounded impact, categorical Stealth, and an expandable telemetry table.
- Corrected BigQuery fine-grained dataset ACL modes, the unaudited v1beta1 connection-IAM path,
  authorized object boundaries, scheduled-query identities and Spark/remote execution; Vertex custom
  code, Agent Engine, endpoint/batch and Workbench identities/access modes; and SCC mute/export,
  detector timing, conditional-IAM, deletion and runtime-shape evasion semantics.
- Removed or folded 19 false, redundant, or miscategorized headings across the three pages. A strict
  heading scan now finds 146/393 qualifying privilege-escalation and 170/391 post-exploitation
  sections rated, leaving 468; persistence remains 153/153.
- This service-page batch used documentation and read-only command/reference checks only. It created
  no cloud resource and made no configuration change.

### 2026-09-28 — API Keys remote MCP list parity verified
- Live-tested `apikeys_list_keys` with disposable minimum-permission service accounts. The supported
  `roles/mcp.toolUser` + `apikeys.keys.list` pair succeeded; the same MCP role without the
  underlying permission reached the wrapper and was denied `apikeys.keys.list`; an underlying-only
  case was denied at the MCP gate. No authorization bypass was found.
- Resource Manager showed the grants before the MCP endpoint accepted them: endpoint-specific IAM
  propagation took roughly 30–90 seconds. Default audit configuration produced no MCP Data Access
  entry for the successful or denied list call. No API key was created or exposed.
- All disposable identities, keys, custom roles, bindings and local configurations from every probe
  attempt were deleted. A final independent inventory check found no `ht-mcp-*` residue.
- A follow-up `tool.name` condition allowed `apikeys_list_keys` and denied `apikeys_get_key` even
  though the principal held both underlying API permissions. Duplicate `params.name` fields in both
  orders showed consistent last-wins authorization/dispatch behavior, so no parser desync was found.
  The conditional binding and every disposable asset were removed and verified absent.
- A `tool.isReadOnly` follow-up corrected the control model: that attribute is deny-policy-only, not
  available for allow bindings. The baseline list/update calls reached the expected service paths,
  but the scoped deny policy could not be created because the lab Owner lacks deny-policy creation.
  No policy or API key was created; all disposable IAM and credential material was removed.

### 2026-09-28 — GKE, Compute post-exploitation, and Cloud Logging audit batch
- Normalized 24 GKE privilege-escalation, 26 Compute post-exploitation, and 17 Cloud Logging
  post-exploitation techniques with explicit minimum prerequisites, Potential Impact, categorical
  Stealth, and expandable per-technique telemetry tables.
- Corrected GKE node-pool authorization, streaming-subresource audit behavior, Workload Identity and
  Connect Gateway constraints; Compute disk/image, serial-console, packet-mirroring, route, NAT/BGP,
  alias-IP and telemetry boundaries; and Logging audit classes, retention/CMEK behavior, linked
  datasets, retroactive copy, and future-only default settings.
- Removed three false standalone GKE escalation headings and the obsolete Logging cross-project
  sink bucket-name hijack. At that batch boundary, a strict heading scan found 121/404 qualifying
  privilege-escalation and 161/399 post-exploitation sections rated; the newer batch above supersedes
  those counts. Persistence remained 153/153.
- This batch was a documentation and official-reference audit. It made no cloud mutation and created
  no test resource.

### 2026-09-28 — Compute privesc and BigQuery post-exploitation audit batch
- Normalized all 15 genuine Compute privilege-escalation sections and all 11 BigQuery
  post-exploitation sections with explicit impact, current least-privilege caveats, categorical
  stealth and per-technique telemetry. Removed Compute's non-technique access-scope placeholder and
  folded its useful context into real metadata/service-account paths.
- Corrected material semantics across project metadata, OS Login, VM Manager, MIGs, disk/image copy,
  BigQuery job metadata, table reads/exports, recovery, DML, transfers, reservations and CMEK.
  These were documentation audits against current official references; they created no cloud asset.
- At that batch boundary, a strict heading scan found 97/407 qualifying privesc and 118/401
  post-exploitation sections rated; the newer GKE/Compute/Logging batch above supersedes these
  counts. Persistence was fully rated at 153/153 under the same scan.
- A live minimum-permission follow-up confirmed that `jobs.listAll/list/get` exposes another
  principal's named query-parameter values through both full-projection list and get, although the
  same values are redacted from audit logs. The synthetic zero-data job metadata was deleted (GET
  then returned 404), and every disposable identity, key, role and binding was verified absent.
- A second live matrix confirmed raw `tabledata.list` works with exactly
  `bigquery.tables.getData`, fails with a partial row policy, and succeeds with a `TRUE` filter.
  Successful pages emitted both canonical and legacy Data Access events; the policy-denied 403 did
  not. The synthetic dataset/table, DDL job metadata and all test IAM/key material were deleted and
  independently verified absent.
- Fine-grained-DML controls found an undocumented discrepancy: two same-age tables both reported the
  feature flag as `YES` and initially allowed `tabledata.list`; after mutating only one, that table
  returned HTTP 400 while the untouched control remained readable. This contradicts the categorical
  documented limitation but did not bypass row/column authorization. All three attempts and every
  disposable asset were cleaned and verified.
- The remaining `tabledata.list` column-policy matrix also enforced the boundary: an untagged-column
  projection succeeded, while tagged and all-column requests returned 403 until the caller received
  Fine-Grained Reader on the policy tag. Successful pages produced both observed BigQuery audit
  formats; denied calls did not appear in that capture. The child tag and taxonomy were explicitly
  deleted and verified 404, and the temporarily enabled Data Catalog API was restored to disabled.

### 2026-09-28 — Secret Manager managed Cloud SQL rotation privesc verified
- Live-verified a new expected permission-composition technique: a caller with exactly
  `secretmanager.secrets.enableManagedRotation`, no Cloud SQL role and no secret-version access can
  choose a Cloud SQL instance, database user and password; the regional secret's built-in identity
  performs the reset. The generated secret version exactly matched the supplied username/password.
- The first successful bounded built-in-identity role contained `cloudsql.instances.get`,
  `cloudsql.users.get/list/update`; the documented `users.list/update` pair had failed earlier. A
  three-versus-four-permission subtraction remains open because the test facilitator's token-mint
  grant had not propagated before that attempt. The book does not mislabel the four-permission set
  as minimal.
- `EnableManagedRotation` produced exact caller-attributed Admin Activity with the single caller
  permission granted; the downstream `cloudsql.users.update` remained absent under default Data
  Access logging. Shipped with impact, minimum permission, Low stealth and a log table to the Secret
  Manager privesc page; added managed-rotation context to service enumeration.
- Three bounded attempts were made while correcting a gcloud regional-parent parsing failure and an
  external quota-project token-mint issue. Every disposable SQL instance/user, regional secret,
  service account, custom role, IAM binding and the temporary Token Creator facilitator binding was
  deleted. Independent queries verified no `ht-smrot-*` instance, identity or project binding.

### 2026-09-26 — BigQuery Engine for Apache Flink resource-model correction
- Corrected all Managed Flink pages to match the current API: jobs carry executable graphs/JARs/
  artifacts, while deployments carry capacity, network, shared-secret and workload-identity
  configuration only. Replaced the false deployment-code/self-restart persistence claim with a
  long-running streaming-job foothold and removed the undocumented metadata-server guarantee.
- Documented deployment identity inheritance, but kept the possible `jobs.create`-without-`actAs`
  path out of privilege escalation because the service's attachment check is not public and the
  preview API is disabled/possibly allowlisted in the lab. Replaced guessed Managed Flink audit
  methods/categories with an explicit telemetry unknown and a controlled validation checklist.
- Added complete impact, minimum-permission, Medium-stealth and expandable logging metadata to the
  retained post-exploitation technique. No API was enabled and no resource/IAM state was created;
  see `managed-flink/tested.md` and `checklist.md`.

### 2026-09-26 — Policy Troubleshooter authorization and telemetry correction
- Removed the nonexistent `policytroubleshooter.troubleshoot` permission and
  `roles/policytroubleshooter.policyReviewer` role from all three relevant pages. Replaced them with
  Google's actual policy/role-read prerequisites and documented `Unknown` behavior when the caller
  cannot inspect every applicable policy, role or group membership.
- Updated examples to the current gcloud/v3 API surfaces, added explicit impact/minimum-permission
  caveats and a High stealth rating, and replaced the unsupported reasoned `DATA_READ`
  `TroubleshootIamPolicy` claim with Google's documented internal IAM `GetEffectivePolicy`
  `ADMIN_READ` signal and an explicit direct-logging unknown.
- The lab API is disabled. Performed only read-only service/role checks, enabled nothing and created
  no resources. See `policy-troubleshooter/tested.md` and `checklist.md`.

### 2026-09-26 — Cloud Scheduler post-exploitation audit correction
- Corrected `GetJob`/`ListJobs` from `DATA_READ` to Data Access `ADMIN_READ` in both the post-
  exploitation and duplicate privilege-escalation coverage. Corrected the latter's unsupported
  get/list-only secret disclosure claim to require `jobs.fullView`, completed minimum permissions
  and categorical stealth metadata for all four post-exploitation techniques, removed an unrelated
  `UpdateJob` row from disruption telemetry and made downstream logging target-method-dependent.
- Clarified that explicitly setting an OAuth/OIDC service account during update requires `actAs`.
  A live attempt to isolate whether a narrow URI-only patch rechecks `actAs` was inconclusive because
  fresh Scheduler grants did not propagate during bounded test windows; it remains in the checklist
  rather than being reported as a vulnerability.
- All paused jobs, temporary identities, keys, bindings and CLI configurations were deleted and
  verified absent. See `cloud-scheduler/tested.md` and `checklist.md`.

### 2026-09-26 — NetApp Volumes post-exploitation boundary correction
- Reduced five claimed techniques to four defensible primitives. Corrected export-policy abuse to
  NFS rather than credentialless NFS/SMB, corrected recovery-point cloning permissions and removed
  an unverified Active Directory password-disclosure candidate from the book.
- Corrected deletion telemetry: volume, snapshot and backup deletion are Data Access `DATA_WRITE`,
  while backup-vault deletion is Admin Activity. Narrowed the ONTAP technique to Google's filtered
  administrator proxy and removed unsupported local-admin/full-cluster-control claims. All four
  retained techniques now have explicit impact, minimum permissions, categorical stealth and log
  tables.
- The lab API is disabled. Sent only a read-only list request, enabled nothing and created no
  infrastructure. See `netapp-volumes/tested.md` and `checklist.md`.

### 2026-09-26 — Cloud Run post-exploitation logging and permission correction
- Completed minimum-permission and stealth metadata for all five Cloud Run post-exploitation
  techniques. Replaced the outdated claim that reads and `RunJob` can never be attributable with
  the current `ADMIN_READ`/`DATA_WRITE` Data Access contract, while retaining the older contrary
  live result as a validation caveat.
- Corrected image recovery to use revision `status.imageDigest`, corrected the nonexistent
  `vpcaccess.connectors.use` permission to the documented connector/network access surface, and
  removed the claim that deleting a Run resource also destroys separately retained logs.
- The lab has no Cloud Run services. Used read-only enumeration and created no infrastructure. See
  `cloud-run/tested.md` and `checklist.md`.

### 2026-09-26 — Certificate Manager post-exploitation quality audit
- Reduced five claimed techniques to three defensible primitives. Corrected self-signed certificate
  substitution from browser-trusted interception to TLS DoS unless a separately trusted cert is
  available; removed redundant DNS-authorization and CA-pool chains that add no capability beyond
  DNS/CA control; and corrected PRIMARY map-entry semantics.
- Corrected Public CA persistence to the non-expiring bound ACME account (the EAB is one-use and
  expires unused after seven days). Its creation is Data Access `DATA_WRITE`, **not logged by
  default**, rather than always-on Admin Activity. All three retained techniques now have explicit
  minimum permissions, stealth ratings and exact log tables.
- Expanded enumeration across certificates, maps and entries, DNS authorizations, issuance configs,
  trust configs, Public CA's create-only surface, permission boundaries and audit visibility.
- Both lab APIs are disabled. Sent only read-only list requests, enabled nothing and created no
  resources. See `certificate-manager/tested.md` and `checklist.md`.

### 2026-09-26 — Service Management / API Gateway rollout-boundary correction
- Corrected the unsupported claim that API Gateway auto-pulls direct Service Management rollouts.
  Managed rollout applies to Cloud Endpoints ESP/ESPv2; API Gateway pins an immutable API config and
  requires a new config plus explicit gateway update. Removed a second unsupported inference that
  the gateway could disclose OAuth access tokens merely because its service-agent role contains
  `getAccessToken`; the documented and verified backend primitive is an audience-bound ID token.
  Corrected Service Management audit method names and completed minimum-permission/stealth metadata
  on both related pages.
- The lab Service Management API is disabled. Made one read-only list request, did not enable it,
  and created no resources. See `service-management/tested.md`/`checklist.md` and
  `api-gateway/tested.md`.

### 2026-09-26 — Cloud Workstations enumeration and logging correction
- Added the missing Cloud Workstations service page covering clusters, configurations,
  workstations, runtime identities, VPC/public exposure, boot code, persistent disks, resource IAM,
  ordinary enumeration and the explicitly unlogged permission-filtered `listUsable` endpoints.
- The authorized lab API is disabled. Sent only a read-only list request, did not enable it, and
  created no infrastructure. Corrected the existing page's `GenerateAccessToken` audit claim and
  added stealth ratings to all three techniques. See `cloud-workstations/tested.md` and
  `checklist.md`.

### 2026-09-26 — Datastream enumeration and false BigQuery-source removal
- Added the missing Datastream enumeration page for profiles, streams/objects, backfills, private
  connectivity/routes and audit visibility. Read-only lab enumeration found no resources; nothing
  was created.
- Corrected a material false claim: BigQuery is a destination, not a Datastream source. The
  credential-free native source technique now covers only Spanner, and conventional-source
  credential/network prerequisites are explicit. Added stealth ratings to all four attack sections.
  See `datastream/tested.md` and `checklist.md`.

### 2026-09-26 — Network Services enumeration and new-surface triage
- Added the missing Network Services enumeration page for meshes/routes, endpoint policy, Service
  Extensions, Agent Gateways, extension bindings and allowlist-gated Cloud Multicast. Linked it from
  the existing Network Services attack page.
- The API is disabled in the authorized lab. Validated current CLI/discovery surfaces and sent only
  read-only list requests; did not enable the API or create infrastructure. Agent Gateway update and
  extension-binding boundaries are tracked as candidates rather than asserted as attacks. Corrected
  the current Editor/Admin role map and added stealth ratings to all six retained Network Services
  attack sections. See `networkservices/tested.md` and `checklist.md`.

### 2026-09-26 — Integration Connectors service enumeration
- Added the missing Integration Connectors service-enumeration page and linked it from both existing
  attack pages. It covers full connection configuration, resource IAM, runtime schemas, events,
  endpoint attachments, managed zones, custom connectors and provider versions, plus exact
  enumeration visibility.
- The installed SDK has no stable `gcloud connectors` group and the authorized lab project's API is
  disabled. Validated the REST paths against Google's current discovery documents and made only
  read-only requests; no API was enabled, no billable connection was created and no teardown was
  necessary. See `integration-connectors/tested.md` and `checklist.md`.

## Completion state per axis

| Axis | State | Notes |
|---|---|---|
| Privesc (existing services) | ✅ complete | Minimum permissions + Potential Impact + "Logs generated" expandable on all 75 privesc pages |
| Post-exploitation (existing) | ✅ complete | Impact + Logs generated on all real post-ex pages (README index exempt) |
| Persistence (existing) | ✅ complete | Logs generated on all real persistence pages (README index exempt) |
| Per-technique stealth ratings | 🟡 in progress | Fresh 2026-09-28 heading scan: 170/311 privesc, 193/364 post-exploitation, 154/154 persistence sections with Impact + Logs generated have a rating; 312 remain in privesc/post-exploitation. Audit service by service against actual log methods and downstream traces. |
| Privesc/post/persistence (net-new services) | ✅ saturated | Multi-phase ground-truth diff of the GCP API surface vs wiki; genuine gaps shipped (Cloud Build staging-bucket poisoning, NetApp ONTAP, Public CA EAB, Discovery Engine ACL, Config Delivery, Integration Connectors, App Engine exportAppImage, SSM sshkeys.createAny, + 6 permission-level) |
| Unauth / recon (all services) | ✅ complete | 13 new per-service pages (baseline 11 → 24); every non-qualifying service verified-excluded via the qualifying rule (`_deferred-and-excluded.md`) |
| Env-var → RCE | ✅ complete | 10 qualifying execution services documented in `environment-variable-injection.md`; all others excluded with reasons |
| `autonomous_research/gcp/` folder | 🟡 in progress | this scaffold; per-service `tested.md`/`checklist.md` being seeded from the audit history |

Page counts (branch `gcp-techniques-audit-2026-09`): **75 privesc · 75 post-ex · 55 persistence ·
25 unauth · 90 service-enum**.

## Standing residue / teardown

- **No standing test residue** as of 2026-09-24. The BigQuery test dataset `ht_bq_ds` (copy/restore
  technique test, created 2026-09-22) and 2 orphaned Gen2 Cloud Functions upload zips were deleted
  and verified gone. All prior-phase test RGs/resources torn down.
- **Persistent lab FIXTURES — do NOT delete as residue** (maintainer's pre-built lab targets,
  created months before this audit): `appengine-lab-1-*` (App Engine app + SA + bucket, 2025/2026-08),
  `kms-lab-1/2/3-*` keyrings incl. `-attacker`/`-victim` (2026-04; KMS keyrings are non-deletable by
  design anyway), `pwn-workflow` (Workflows, 2026-06), `cloudfunction-lab-1/2/3` sources in the
  platform `gcf-sources-*` staging bucket (has a `DO_NOT_DELETE_THE_BUCKET.md` marker).

## Method (how completeness was argued)

- **Ground-truth API diff** — botocore-equivalent GCP API models / `gcloud` service surface diffed
  against the wiki corpus to find services/permissions with no coverage (see
  `gcp-wiki-gap-analysis-method` memory).
- **Technique fan-out** — three converging hunters over the authenticated surface (IAM/credentials,
  compute/GKE, storage/serverless/build/data) → one gap (Cloud Build staging bucket), shipped.
- **Unauth sweep** — 5 hunters applying the qualifying rule across all services.
- **Env-var RCE closure** — full execution-service roster, 10 qualifying + reasoned exclusions.
- **Live-fire** where the lab allows (owner on `gcp-labs-eqd4ny8d`); doc-grounded where blocked by
  the cost/permission/org-access exceptions.

## Known open items (tracked as per-service checklists)

Seeded into `<service>/checklist.md`. The eternal loop: when a checklist item is tested it moves to
that service's `tested.md` with the result (and, if it works and is non-duplicate, to the wiki);
when no checklist items remain, generate more non-duplicate candidate ideas.

## Loop iteration log

### 2026-09-24 — batch 1 (initial seeded backlog worked through)
- **Dataplex `tasks.update` actAs-bypass** — live-tested, **REJECTED**: update re-validates
  `iam.serviceAccounts.actAs` on the bound SA for any field, like create. No privesc.
- **Pub/Sub GCS import-topic injection** — live-tested, **SHIPPED**: standing message-injection /
  persistence via `topics.create`/`update` ingestion source (attacker bucket → all subscribers).
- **Artifact Registry `exportArtifact`** — API-verified, **SHIPPED**: reader-level server-side exfil
  to arbitrary GCS bucket.
- **Closed as verified duplicates (already documented, no ship):** ACM `replaceAll` teardown,
  SCC scanner/mute-config evasion, IAP tunnel egress, Secret Manager managed-rotation misuse,
  Cloud Build gen2 `repositories.create` (execution still gated by triggers+actAs).
- **Resolved:** the official Org Policy audit table confirms v2 CreatePolicy/UpdatePolicy are
  always-on Admin Activity; legacy v1 setOrgPolicy logs under Cloud Resource Manager instead.
- Backlog empty → generating new candidate batch (WIF federation, Storage Transfer confused-deputy,
  BQ Data Transfer scheduled-query persistence, Cloud Asset exportAssets, Backup&DR, Datastream).

### 2026-09-24 — batch 2 (named-candidate brainstorm) — 12 candidates, ALL already documented
- Checked (all COVERED, no ship): WIF pool/provider backdoor, Storage Transfer confused-deputy,
  BQ Data Transfer scheduled-query persistence, Cloud Asset exportAssets, Backup&DR anti-recovery,
  Datastream CDC exfil, Certificate Authority Service (leaf+subordinate), Cloud DNS response-policy
  MITM, Eventarc Advanced pipelines/messagebus, Certificate Manager trust-config poisoning,
  Cloud Billing detach-DoS/bill-shift, Service Directory endpoint poisoning.
- **Conclusion:** the wiki is at saturation for named/well-known primitives. Switched method to a
  ground-truth permission-surface diff (per `gcp-wiki-gap-analysis-method`).

### 2026-09-24 — batch 3 (ground-truth permission diff) — found a real gap
- Diffed all 13,681 project-testable permissions' service prefixes against the wiki text; triaged the
  zero-mention prefixes. Most are niche/managed/analytics/preview (no attack primitive).
- **GAP FOUND & SHIPPED:** Service Extensions **`networkservices.authzExtensions.*`** (+ siblings
  `lbEdgeExtensions`, `swpSecurityExtensions`) had zero wiki mention — the existing Service Extensions
  section covered only traffic/route/WASM extensions. Added the ext_authz authorization-callout hijack
  (auth bypass / per-request credential exfil / DoS) to `gcp-networkservices-privesc.md`.
- Ground-truth diff is the productive method at this maturity; named-candidate brainstorming is not.

### 2026-09-24 — batch 4 (permission-level + resource-type diff) — found a real gap
- Refined the diff from service-prefix to **individual write-permission** and then to **resource-type
  token** (4,428 write-perms → 3,624 undocumented strings → 845 zero-mention resource types).
- Found the string-level diff has false positives (wiki covers the *concept* w/o the exact dotted
  perm): IAM deny policies, NSI packet-mirroring/intercept, SCC detector-disable, NGFW
  firewallEndpoints all re-confirmed **already covered** — even the newest NSI
  intercept/mirroring endpoint groups are documented (`gcp-ids-post-exploitation.md`).
- **GAP FOUND & SHIPPED:** IAM **`oauthClients`** / **`oauthClientCredentials`** (Workforce Identity
  Federation OAuth clients, GA 2024) had zero wiki coverage (all "oauth client" mentions are DWD
  client-id or IAP `clientauthconfig`). Live-verified the attacker-controlled half (create client +
  secret, cloud-platform scope, attacker redirect URI, plaintext-secret readback, **invisible to the
  project IAM allow policy**); shipped as a project-level workforce-federation persistence backdoor
  in `gcp-workload-identity-federation-persistence.md`. Test infra torn down.
- Method note: resource-type-token diff (not just service-prefix) is where remaining gaps live —
  undocumented *sub-resources within already-documented services*.
- **2nd GAP FOUND & SHIPPED (same batch):** **`networkservices.googleTagGatewayPolicies`** (Google
  Tag Gateway / "first-party mode", zero wiki mention). `perDomainConfig[].tagId` +
  `performTagInitialization` let an attacker with `googleTagGatewayPolicies.create`/`update`
  (roles/networkservices.editor|admin, editor/owner) make the external Application LB serve an
  attacker-controlled GTM container **first-party** → arbitrary JS on every visitor, CSP-bypassing,
  invisible to app code. Shipped to `gcp-networkservices-privesc.md` with explicit alpha/preview +
  not-live-verified caveats (perm confirmed in roles; resource is v1alpha1 REST-only).
- Re-confirmed covered/niche (no ship): GKE Backup cross-project channels (cross-project
  backup/restore exfil already documented across Filestore/Firestore/Spanner/NetApp), KMS
  `kajPolicyConfigs` (KAJ "zero access reasons" lockout already on the KMS post-ex page), Storage
  Insights datasetConfigs, Developer Connect (35 mentions).
- **This iteration shipped 3 real gaps** (authzExtensions, iam.oauthClients, googleTagGatewayPolicies)
  from the ground-truth diff. Remaining zero-mention resource types are ML/analytics/SOAR internals
  or covered-concept plumbing.
- Then ran two more diff axes + a fresh-catalog delta to confirm exhaustion: **setIamPolicy/use/actAs**
  diff (compute LB internals, all covered-concept), **credential/token-mint** diff (only irrelevant
  `fpnv.phoneNumberTokens.*` undocumented; every real token-mint primitive covered), and a **fresh
  testable-permissions pull** (13,698 vs 13,681 — only 21 new perms since session 8, none
  attack-relevant: compute.regionSslPolicies.setIamPolicy, dataplex.entryLinkTypes.*, AI noise).
  Added an Instant Snapshots NOTE to compute post-ex (distinct perm, same exfil family — not a
  duplicate technique).
- **Saturation is genuine across six axes.** Open frontier + monitoring cadence recorded in
  `autonomous_research/gcp/_frontier.md`. Next iterations: re-pull the catalog periodically and
  triage newly-GA/preview sub-resources (the productive vein); live-verify the two deferred
  end-to-end items (tag-gateway JS injection, oauthClients token-exchange) if the infra becomes
  standable. Do NOT manufacture marginal techniques to fill the loop — ship only real gaps.

### 2026-09-25 — batch 5 (fresh catalog delta + one confirmation + one fold)
- **Catalog re-pull:** 13,701 project-testable permissions (+3 vs the 13,698 of batch 4). The delta is
  AI/analytics/preview noise — no attack-relevant primitive. Ground-truth surface remains **saturated**.
- **CONFIRMED & wiki-upgraded — Cloud SQL pg_cron in-engine scheduled-task persistence.** Stood up a
  throwaway POSTGRES_15 db-f1-micro, `cloudsql.enable_pg_cron=on` + `cron.schedule`, verified the job
  fires every minute with no client session, survives IAM revocation + restart. Upgraded
  `gcp-cloud-sql-persistence.md` from "not live-verified" to confirmed; sharpened min-perms
  (`cloudsql.instances.update` + `cloudsqlsuperuser` DB login; connect optional) and logs (only the
  flag write hits Admin Activity; recurring exec is engine-internal, no Cloud Audit Log). Instance
  deleted, teardown verified. See `cloud-sql/tested.md`.
- **FOLD (not a new technique) — PSC producer-authz.** `networkconnectivity.pscAuthorizationPolicies` /
  `serviceConnectionMaps` is a parallel producer-side authz family to the documented PSC consumer
  accept-list. Added as a FOLD note bullet to `gcp-vpc-and-networking.md`. See `networkservices/tested.md`.
- **REJECTED — multicloud data-transfer.** Storage Transfer / BQ multicloud configs pull INTO the
  project (attacker must already own the source); no new exfil primitive. No ship.
- **New open lead (cost-light, next iteration):** Managed Workload Identity
  `managedIdentities.addAttestationRule`/`setAttestationRules` as a `setIamPolicy`-free membership
  backdoor (analogous to the shipped `iam.oauthClients` workforce backdoor). WIF `providerKeys`
  (SAML-decrypt-only) and `namespaces` assessed and dismissed as non-primitives. See
  `iam-and-credentials/checklist.md`.
- **This iteration shipped:** 1 confirmation-upgrade (Cloud SQL pg_cron) + 1 fold note (PSC). No
  marginal techniques manufactured. Loop continues.

### 2026-09-25 — batch 6 (worked the batch-5 lead) — 1 REAL gap SHIPPED
- **Managed Workload Identity attestation-rule membership backdoor — SHIPPED (live-verified control
  plane).** The batch-5 lead paid off. A principal with only the attestation-rule write
  (`workloadIdentityPoolManagedIdentities.setAttestationRules`, or `roles/iam.workloadIdentityPoolAdmin`,
  **no `setIamPolicy` anywhere**) enrolls an attacker workload into a privileged managed identity; the
  membership is **invisible to `getIamPolicy`** (managed-identities/namespaces have no get-iam-policy
  surface). Not a duplicate — zero prior wiki coverage of Managed Workload Identity / attestation rules.
  Shipped to `gcp-workload-identity-federation-persistence.md`. Rule write is Admin-Activity-logged;
  membership + downstream token mint are not. Full teardown verified (pool tombstoned, all else deleted).
- Corrected the permission string (guessed `iam.managedIdentities.addAttestationRule` was wrong; real =
  `iam.googleapis.com/workloadIdentityPoolManagedIdentities.setAttestationRules`).
- **This iteration shipped 1 real gap.** Loop continues; frontier updated (lead resolved).

### 2026-09-25 — batch 7 (next-lead gap-hunt) — NOTHING SHIPPABLE (saturation re-confirmed)
Read-only whole-service gap scan (317 service prefixes, zero-mention triage on identity/exec-relevant
ones; catalog still 13,701). No genuinely-uncovered cost-light primitive found. Ruled out (record for
dedup — do NOT re-chase):
- **`iamconnectors.connectors.retrieveCredentials`** — DUPLICATE: `iamconnectors.*` is the backend twin
  namespace of the **Agent Identity auth-manager** (`agentidentity.*`), already documented in
  `gcp-agent-identity-auth-manager-privesc.md`. The public API is `agentidentity.googleapis.com`
  (`iamconnectors.googleapis.com` 404s). Same retrieveCredentials-vault-read / token-endpoint concept.
- **`dataprocrm.nodes.mintOAuthToken`** — REJECT: internal node↔control-plane protocol method, no public
  REST/gcloud, mints for the calling node's own identity. Backend-protocol only (0-day-class if at all).
- **`cloudsql.instances.createTestingAgentSession`** — REJECT: `create` only in `cloudsql.admin` (already
  full DB compromise); get/list/cancel are Gemini-in-DB agent-session control, no new lever.
- **`aiplatform.sandboxEnvironments.execute` / `extensions.execute` / `sessions.run`** — REJECT
  (false-positive gap): Google-managed sandboxes, no project SA on metadata server. Real Vertex run-as-SA
  family (customJobs/pipelineJobs/reasoningEngines/tuningJobs/... all actAs-gated) fully documented.
- **`firebaseauth.users.createSession` / `firebasedataconnect.connectors.impersonateQuery`** — DUPLICATE:
  session-cookie mint / custom-token / Data Connect end-user impersonation all in the Firebase pages.
- **`confidentialcomputing.challenges.*`** — REJECT: Confidential Space attestation → WIF; needs a real
  TEE VM (not cost-light) and token only issues against genuine hardware evidence (abuse = attestation
  0-day, out of scope).
- **`networkmanagement.providers.generateProviderAccessToken` / `developerconnect...generateGitHubStateToken`**
  — REJECT: niche NGFW-integration token / OAuth CSRF state token, not credentials.
- Whole-service gaps `remotebuildexecution`/`workloadmanager`/`saasservicemgmt`/`runapps`/`dataprocessing`
  + Maps/retail/commerce — no actAs-free exec-as-SA, token-mint, or IAM self-grant primitive.
**No ship. No lab resources created (read-only). Do not manufacture marginal techniques.** Next iteration
= periodic catalog re-pull + newly-GA/preview sub-resource triage (the productive vein), best after a
delay for the API surface to actually change. Loop stays alive.

### 2026-09-26 — Secret Manager stealth audit
- Reconciled all 12 Secret Manager privesc/post-exploitation headings against their existing audit-event tables and the current Google audit-logging reference. Added 9 missing per-technique stealth ratings; 1 regional-CMEK rating and 2 persistence ratings already existed. No new technique was warranted.
- Documentation-only pass: no GCP API mutations, spend, or teardown required. Recorded details in `secret-manager/tested.md`. Next iteration: choose another service with missing ratings, or triage genuinely new API resources in the permission catalog.

### 2026-09-26 — Cloud Tasks audit-log correction
- The current Google audit reference explicitly excludes `CreateTask` from Cloud Audit Logs even with Data Access logging enabled. Corrected the three Cloud Tasks pages; `RunTask` is `DATA_WRITE` rather than `DATA_READ`. Queue Admin Activity events remain always logged, and dispatch platform logs require queue sampling. These distinctions matter for incident response and stealth ratings.
- Added 11 missing per-technique stealth ratings across the Cloud Tasks privesc and post-exploitation pages; all three persistence headings already had ratings. Documentation/prior-evidence review only; no lab resource created. See `cloud-tasks/tested.md` and `cloud-tasks/checklist.md`.

### 2026-09-26 — permission catalog and Parameter Manager review
- Fresh `list-testable-permissions` pull: **13,701** project-testable permissions, unchanged in count from batch 7. Triaging credential/token names found no immediately shippable permission-level gap; `backupdr.bvdataSources.fetchAccessToken` is documented as internal-only and returns a downscoped backup-location token, so it remains an untested candidate rather than a book entry.
- Rechecked Parameter Manager's newer template/tag features and audit classifications; both post-exploitation techniques now have explicit stealth ratings. No new primitive or lab infrastructure for this review.

### 2026-09-26 — Secure Source Manager audit correction
- Google's SSM audit table classifies Git fetch as `DATA_READ` and Git push plus `CreateAnySshKey` as `DATA_WRITE`, all disabled by default. Corrected the prior book claims that fetch/push had no Cloud Audit method and cross-identity SSH-key creation was always-on Admin Activity. Added stealth ratings across five privesc sections; flagged branch-rule/hook/link audit mappings as unverified instead of inventing a log category. No SSM infrastructure created; see `secure-source-manager/tested.md`.

### 2026-09-26 — Cloud Run visibility sweep
- Added stealth ratings to all 13 Cloud Run privesc sections using the page's prior live audit captures: create/update/IAM changes are attributable Admin Activity, while `run.jobs.run` and overrides emit an unattributed System Event and template reads have no audit entry even with Data Access on. The allowlist-gated SSH path remains explicitly provisional. Reviewed the new Cloud Run instances preview: ordinary `instances.create` + `actAs` duplicates the known Run-as-SA family; investigate update/start boundaries before adding a technique. No new Run resource was created; see `cloud-run/checklist.md`.

### 2026-09-26 — Cloud Run instance update boundary tested
- On a disposable preview instance, a caller holding only `run.instances.update` could not alter the container environment while keeping the attached identity unchanged: HTTP 403 specifically denied `iam.serviceaccounts.actAs`. The failed `v2.Instances.UpdateInstance` was attributable in Admin Activity with `status.code=7`. This closes the unchanged-identity update lead; added the variant and its log shape to the existing Cloud Run update page, without a duplicate technique. The instance, test identities, binding, and custom role were removed and checked absent; see `cloud-run/tested.md`.

### 2026-09-26 — Agent Identity update boundary tested
- A preview Cloud Run service with `identity-type=agent-identity` still carried the Compute Engine default service account in its revision template. A caller with only `run.services.update` could not alter the container environment: the v2 API denied missing `iam.serviceAccounts.actAs` on that default SA and logged the failure with the caller. The first deployment failed at a preview certificate mount; retrying with `--no-identity-certificate` started successfully. Both services and all test IAM objects were removed; Agent Registry/App Hub APIs were returned to their prior disabled state. No new privesc technique; see `cloud-run/tested.md`.

### 2026-09-26 — IAP false-positive removal
- Google's IAP guidance confirms an OAuth client secret does not grant IAP IAM authorization, and the IAP OAuth Admin API is retired. Removed the three book claims that treated `clientauthconfig.*` access as a standalone privesc/persistence backdoor, including the obsolete standalone page. Added four stealth ratings to the retained IAP privesc sections and changed unsupported "runtime never audited" claims to unverified because the published method table only omits them. Corrected the resource-IAM persistence PoC to call IAP `iap_tunnel/...:setIamPolicy` rather than modifying the unrelated Compute VM IAM policy. No lab resource created; see `iap/tested.md`.

### 2026-09-26 — Cloud SQL audit and technique review
- Corrected the Cloud SQL post-exploitation and persistence audit tables against Google's current method reference: user create/update, database delete, export, and import are Data Access methods, disabled by default. Fixed the mistaken user-create and backup-restore method names, added a stealth rating to all 17 retained post-exploitation sections, and recorded the proxy's Admin Activity connection method.
- Removed unsupported direct backup-to-GCS and CMEK-key-repoint techniques. The published backup-export permission is documented for an AlloyDB migration, and the CMEK re-encryption method rotates to a version of the existing key. Clarified extra permissions for the end-to-end clone/replica database access paths. The live regional-secret managed-rotation test is being tracked separately in `secret-manager/tested.md`; its Cloud SQL instance and other first-round resources were verified deleted.
- Reviewed Cloud Run delayed jobs Preview: delay changes execution timing, with no distinct permission or persistence primitive beyond existing job execution. No delayed job was launched.

### 2026-09-26 — AlloyDB Studio and visibility review
- Google's Studio guide requires database authentication and database-level grants even for API-executed SQL. Corrected the page's earlier password-free / viewer-only DB-access claim; `roles/alloydb.viewer` holding `executeSqlReadOnly` is insufficient by itself to establish a database identity. The v1 audit table lists a `users.login` check for `ExecuteSqlReadOnly` and classifies `ExecuteSql` as `DATA_WRITE`. Added stealth ratings to all six AlloyDB post-exploitation sections. No AlloyDB infrastructure was created; see `alloydb/tested.md` and `checklist.md`.

### 2026-09-26 — Database Migration Service prerequisite review
- Corrected the DMS exfil page to require a usable source connection profile, source database privileges, destination setup, and network reach. Removed the unsupported claim that `roles/editor` alone guarantees arbitrary victim database exfil and the duplicate section that inferred arbitrary Cloud SQL/AlloyDB API calls from the broad DMS service-agent role. The `--dump-path` flag is a dump *source* in relevant modes, not a generic exfil sink. No migration infrastructure created; see `database-migration/tested.md`.

### 2026-09-26 — Cloud KMS visibility and Autokey prerequisite review
- Added explicit stealth ratings to all five KMS privilege-escalation and nine post-exploitation techniques. Crypto-use operations are high-stealth under default logging (`DATA_READ`, off by default); lifecycle/configuration writes are lower-stealth Admin Activity, with Autokey split across folder, resource-project, and key-project scopes.
- Corrected the Autokey repoint minimum permissions: the caller needs `cloudkms.autokeyConfigs.update` on the parent and `cloudkms.cryptoKeys.setIamPolicy` on the proposed key project. This preserves the attacker-owned-project custody path but removes the implication that the folder permission alone can choose an arbitrary destination. No GCP resource was created; see `kms/tested.md`.

### 2026-09-26 — Cloud Run cached-image export verified
- Discovered and live-verified `run.locations.exportImage`: a custom-role principal holding only that permission, no revision-read permission, and no Artifact Registry access exported the immutable image behind a known Cloud Run revision to a chosen Artifact Registry package path. Repeating from a revision backed by a private image confirmed that source-repository read access is not checked.
- The server-side uploader is the source project's Cloud Run service agent; granting Artifact Registry Writer to the caller failed, while granting Writer only to `service-<SOURCE_PROJECT_NUMBER>@serverless-robot-prod.iam.gserviceaccount.com` succeeded. The API calls are `DATA_READ` and produced no entry under default logging. All test resources, bindings, credentials, and local key material were deleted and verified absent; see `cloud-run/tested.md`.

### 2026-09-26 — Cloud Run Worker Pool boundary and logging corrections
- Confirmed that an existing worker pool cannot be modified with `run.workerpools.update` alone: a container-only patch by a principal lacking `actAs` was denied on the unchanged default service account, with both the failed update and IAM check attributed in Admin Activity.
- Corrected worker-pool detections to use the live `cloud_run_worker_pool` resource type. Current `gcloud run worker-pools deploy` creates via `UpdateWorkerPool` + `allowMissing:true` and checks both create/update, so matching only `CreateWorkerPool` misses CLI-created pools. The continuously billed test pool and all IAM/credential artifacts were removed and verified absent; see `cloud-run/tested.md`.

### 2026-09-26 — low-value technique removal
- Removed three standalone entries that failed the book's usefulness bar: Bigtable authorized-view creation (requires the same base-table access it would expose), Cloud Functions update without `actAs` (denied even for unchanged-identity patches), and Cloud Functions `generateUploadUrl` alone (stages an object but cannot change a function). Negative results are retained in `_deferred-and-excluded.md`; the real update+`actAs`, authorized-view update/read, and source-deploy chains remain documented.

### 2026-09-26 — Cloud Tasks service-enumeration page
- Added the missing Cloud Tasks enum page with location-wide queue discovery, queue configuration/IAM/CMEK inspection, task `BASIC`/`FULL` inspection, security-review cues, logging visibility, and links to privesc, post-exploitation, persistence, and unauthenticated-access pages. Live read-only checks confirmed the location field and queue activity-log identifiers. Removed duplicate secret-read and queue-DoS entries from privesc; their authoritative post-exploitation entries remain. No resource or configuration was changed. See `cloud-tasks/tested.md`.

### 2026-09-26 — identity-federation service-enumeration page
- Added a unified service page for classic workload pools/providers, org-scoped workforce pools/providers, project-scoped workforce OAuth clients/credentials, and managed workload identities/attestation rules. The page joins trust configuration to IAM principal bindings and explicitly inventories soft-deleted/revivable resources and membership surfaces absent from `getIamPolicy`. Read-only live checks validated the project-level commands; no GCP state changed. See `iam-and-credentials/tested.md`.

### 2026-09-26 — Apigee enumeration and historical-vulnerability correction
- Added the missing authenticated Apigee service-enumeration page across ingress, proxy/shared-flow deployment, backend routing, credentials/secrets, trace/debug and resource-IAM surfaces. The lab has no accessible Apigee organization, so only credential-wide organization listing was live-run; no resource was created.
- Corrected the post-exploitation page: `GatewayToHeaven` is CVE-2025-13292, fixed for managed Apigee in `1-16-0-apigee-3` per GCP-2026-010. Consolidated five current-looking chain steps into one historical/unpatched-Hybrid technique with the official remediation floor, impact, stealth and logs. See `apigee/tested.md`.

### 2026-09-26 — SUMMARY navigation audit
- Added the two existing GCP technique pages omitted from the category navigation: Pub/Sub post-exploitation and Storage persistence. Both pages were already reachable from service content; this change makes them visible in their complete post-exploitation and persistence trees.
- Documentation-only correction; no GCP API call or resource mutation was required.

### 2026-09-26 — Access Context Manager and Org Policy metadata/correctness audit
- Added exact minimum permissions, categorical stealth ratings, and expandable audit-event tables to all seven Access Context Manager and four Organization Policy techniques.
- Corrected two material scope/logging errors: folder/project IAM grants do not confer ACM policy access (authority must come from the organization or target access-policy IAM, and Organization Admin has no ACM permissions); legacy v1 Org Policy writes log under `cloudresourcemanager.googleapis.com`, while v2 uses `orgpolicy.googleapis.com`.
- Verified current predefined-role contents with read-only `gcloud iam roles describe` calls and current official audit/access-control references. No GCP resource or configuration was changed.

### 2026-09-26 — Access Approval metadata and audit-method review
- Added minimum permissions and stealth ratings to both Access Approval post-exploitation techniques, and replaced inferred method names with Google's fully qualified audited methods.
- Recorded the useful visibility boundary: settings/request mutations are always-on Admin Activity, while the corresponding get/list reconnaissance methods produce no audit log. No cloud resource or setting was changed; see `access-approval/tested.md`.

### 2026-09-26 — Pub/Sub post-exploitation quality and visibility audit
- Completed minimum-permission and stealth metadata for all 16 retained Pub/Sub post-exploitation techniques. Corrected message operations to “never audited” and `Seek` to Data Access `ADMIN_READ` (off by default, auditable when enabled), matching both the current official method table and the prior live research record.
- Removed two entries below the book's quality bar: schema deletion was explicitly documented as useless for validation bypass, and schema IAM self-grant had no standalone impact outside the already documented schema-attachment chain. No cloud resource was created; see `pub-sub/tested.md`.

### 2026-09-26 — unauthenticated-technique service navigation audit
- Added missing service-page links to the existing unauthenticated-access pages for API Gateway, BigQuery, Bigtable, Cloud DNS, Firebase, IAP, Pub/Sub, and Secret Manager. Also restored the missing Firebase and Pub/Sub privilege-escalation links.
- Verified every new mdBook ref target locally. Navigation-only change; no cloud API call or resource mutation was needed.

### 2026-09-26 — service-to-technique crosslink audit
- Restored 37 missing links from 15 existing service-enumeration pages to their matching privesc, post-exploitation, and persistence pages: Config Controller, Bare Metal Solution, Looker, Managed Kafka, VMware Engine, VM Migration, BigLake, NetApp Volumes, Container Analysis, Cloud Deploy, Spanner, Eventarc, Contact Center Insights, Document AI, and Managed Flink.
- Added only links whose target pages exist and verified every relative target locally. Navigation-only change; no cloud API call or resource mutation was needed.

### 2026-09-28 — permission delta and API Keys MCP frontier
- A fresh read-only project permission pull returned **13,701**, unchanged from the 2026-09-25
  baseline. Official release notes after the baseline contain only Google SecOps SOAR maintenance;
  no new IAM permission or directly shippable GCP attack primitive was found.
- Reviewed the boundary-day API Keys remote MCP Preview. It adds the `mcp.tools.call` wrapper but no
  new `apikeys.keys.*` capability. Recorded private candidates for underlying-permission parity,
  MCP conditional/cross-project policy enforcement, the `apikeys_update_key` risk hint, and MCP audit
  shape in `api-keys/checklist.md`/`tested.md`. No speculative book technique was added.
- Documentation plus read-only discovery only: no API was enabled and no cloud resource, IAM policy,
  key, or local credential was created or changed.

### 2026-09-28 — Dataproc and Cloud Storage visibility/correctness batch
- Added explicit categorical stealth ratings to all 11 Dataproc privilege-escalation techniques and
  all 14 Cloud Storage post-exploitation techniques. A fresh scan, which also incorporates the many
  intervening 2026-09-26 service batches and the new managed-rotation technique, finds 617 qualifying
  privesc/post-exploitation sections still unrated.
- Corrected substantive boundaries rather than only adding labels: narrowed cluster-level Dataproc
  IAM self-grant to callers that already hold project-level job creation; replaced the unsupported
  custom-container `ENTRYPOINT` claim with dependency/environment poisoning; corrected Serverless,
  Component Gateway, OS Login and staging-object prerequisites; and accounted for driver/gateway/
  guest/downstream telemetry.
- Corrected Cloud Storage public-read and lifecycle audit exclusions, HMAC/IP-filter/restore method
  boundaries, signed-URL duration, soft-delete/versioning recovery semantics, Batch Operations scope,
  detailed-audit-mode caveats and reversible versus permanent CMEK denial.
- Documentation and official-reference review only; no Dataproc or Storage resource was created.
  Detailed results and remaining validation questions are in `dataproc/` and `storage/`.
