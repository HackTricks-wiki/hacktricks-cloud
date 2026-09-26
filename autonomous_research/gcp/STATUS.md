# GCP audit — status

Last updated: 2026-09-26

## Completion state per axis

| Axis | State | Notes |
|---|---|---|
| Privesc (existing services) | ✅ complete | Minimum permissions + Potential Impact + "Logs generated" expandable on all 75 privesc pages |
| Post-exploitation (existing) | ✅ complete | Impact + Logs generated on all real post-ex pages (README index exempt) |
| Persistence (existing) | ✅ complete | Logs generated on all real persistence pages (README index exempt) |
| Per-technique stealth ratings | 🟡 in progress | As of 2026-09-26: 43/403 privesc, 33/405 post-exploitation, 156/156 persistence headings with Impact + Logs generated have a rating; 732 remain in privesc/post-exploitation. Audit service by service against actual log methods and downstream traces. |
| Privesc/post/persistence (net-new services) | ✅ saturated | Multi-phase ground-truth diff of the GCP API surface vs wiki; genuine gaps shipped (Cloud Build staging-bucket poisoning, NetApp ONTAP, Public CA EAB, Discovery Engine ACL, Config Delivery, Integration Connectors, App Engine exportAppImage, SSM sshkeys.createAny, + 6 permission-level) |
| Unauth / recon (all services) | ✅ complete | 13 new per-service pages (baseline 11 → 24); every non-qualifying service verified-excluded via the qualifying rule (`_deferred-and-excluded.md`) |
| Env-var → RCE | ✅ complete | 10 qualifying execution services documented in `environment-variable-injection.md`; all others excluded with reasons |
| `autonomous_research/gcp/` folder | 🟡 in progress | this scaffold; per-service `tested.md`/`checklist.md` being seeded from the audit history |

Page counts (branch `gcp-techniques-audit-2026-09`): **75 privesc · 75 post-ex · 55 persistence ·
25 unauth · 89 service-enum**.

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
- **Deferred (verification-only):** Org Policy v2 CreatePolicy/UpdatePolicy audit-class check.
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

### 2026-09-26 — low-value technique removal and Cloud Functions audit-integrity report
- Removed three standalone entries that failed the book's usefulness bar: Bigtable authorized-view creation (requires the same base-table access it would expose), Cloud Functions update without `actAs` (denied even for unchanged-identity patches), and Cloud Functions `generateUploadUrl` alone (stages an object but cannot change a function). Negative results are retained in `_deferred-and-excluded.md`; the real update+`actAs`, authorized-view update/read, and source-deploy chains remain documented.
- Preserved the unexpected finding from the upload-URL test as a private report: Cloud Functions v1 records `cloudfunctions.functions.sourceCodeSet` as granted even when a minimum-permission caller held only `cloudfunctions.functions.generateUploadUrl`; v2 records the correct permission. The report and reproducible PoC are in `$HOME/cloud_bb/gcp/cloud-functions-v1-generateuploadurl-false-authorizationinfo.md`. No new resource was created in this review; the original test identity and upload artifacts were already removed.
