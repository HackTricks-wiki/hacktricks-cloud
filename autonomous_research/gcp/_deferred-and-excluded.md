# GCP — deferred & excluded (verified reasoned exclusions)

Services/primitives that were **checked and deliberately NOT given a page/technique**, with the
reason. Recorded so no future agent re-tests them. Re-open only if the service's IAM/data-plane
surface materially changes.

## Unauthenticated / external-attacker axis — verified NO page needed

Qualifying rule: a service needs an unauth page iff it has resource-level IAM accepting
`allUsers`/`allAuthenticatedUsers` **and** an outsider-reachable data plane. These fail one side:

| Service | Why no unauth page |
|---|---|
| GKE | Generic Kubernetes exposure — covered by generic k8s pages, not a GCP-IAM unauth surface |
| Cloud Composer / Dataproc / Dataflow | Web UIs are IAP-gated / not anonymously reachable |
| Vertex AI / Cloud Workstations / Looker (core) | IAP-gated; no anonymous data plane |
| Vertex AI prediction endpoints | Cannot be made public/anonymous |
| Eventarc / Cloud Tasks* / Cloud Scheduler / Workflows | No anonymous listener (they *call out*, don't accept anon in) |
| Cloud Source Repositories | Structurally refuses `allUsers` bindings |
| Memorystore / AlloyDB / Cloud SQL | Protocol-level (Redis/Postgres/MySQL wire), not a REST+IAM data plane that accepts `allUsers` |
| Cloud KMS | No public/anonymous data plane |
| Document AI / Vision / Speech / Translation | No per-resource IAM accepting `allUsers` |
| Cloud Deploy / Container Analysis / Batch / Life Sciences | No resource-level IAM accepting `allUsers` |

\* Cloud Tasks **does** have an unauth page — the `cloudtasks.tasks.create`→`allUsers` enqueue
surface qualifies (task injection/SSRF). The "no anon listener" note above refers only to it not
accepting inbound anonymous *delivery*.

**Shipped unauth pages (24 total, baseline 11 → +13 this audit):** API Keys, App Engine, Artifact
Registry, Cloud Build, Cloud Functions, Cloud Run, Cloud SQL, Compute, IAM/Principals/Org, Source
Repos, Storage (+Public Buckets subpage), Cloud DNS, Google Groups, BigQuery, Firebase, Pub/Sub,
API Gateway, Apigee, Cloud Endpoints, Looker Studio, Healthcare API, Secret Manager, Cloud Tasks,
Bigtable, IAP.

## Env-var → RCE axis — excluded execution services

**Excluded because direct code/command/image/source exec is the native, simpler path (an
env-var-specific row would be redundant garbage — each already documents the direct RCE):**
Cloud Build, Dataproc + Dataproc Serverless, Dataflow classic, Dataform, Cloud Deploy, Cloud
Workstations, Cloud Shell, Apigee, Data Fusion, Vertex AI notebooks/notebookExecutionJobs/
pipelines/Colab Enterprise, Application Integration, Config Controller.

**Not executors (env-var RCE N/A — run no user interpreter):** Cloud Scheduler, Cloud Tasks
(call HTTP endpoints), Eventarc, Pub/Sub (routing; deliver to Run/Functions which ARE covered),
Workflows (YAML DSL, no interpreter-startup var), Cloud SQL / AlloyDB / Spanner / Bigtable /
Firestore (DB engines — in-engine code is DB-native e.g. pg_cron/extensions, covered under DB
persistence), Transcoder / Live Stream / Healthcare / DICOM (managed processing, no user code).

**Qualifying env-var→RCE services (10, all documented in `environment-variable-injection.md`):**
Cloud Run services, Cloud Run jobs, Cloud Composer, Cloud Functions gen1+gen2, GCP Batch, Dataflow
Flex Templates, Vertex AI custom jobs, App Engine versions, GKE workloads (BinAuthz bypass),
Firebase App Hosting.

## Discovery-axis exclusions (net-new service pages considered, not added)

Every service in the botocore-equivalent GCP API surface was diffed against the wiki. Services with
no distinct abusable primitive beyond existing coverage, or that are retired/preview/niche, were not
given pages. (See `gcp-technique-audit-progress` memory for the full ground-truth diff record.)

## Technique-level exclusions (tested but not useful enough for the book)

| Service / primitive | Result and exclusion reason |
|---|---|
| Bigtable `bigtable.authorizedViews.create` | **Excluded from post-exploitation.** Creating a view also requires base-table read and mutate access, and making it accessible to a new principal additionally requires `bigtable.authorizedViews.setIamPolicy`. The view cannot expose data beyond its own subset, so this adds no meaningful capability over the caller's existing base-table access. Keep the real `authorizedViews.update` boundary-broadening technique in the privesc page. |
| Cloud Functions `cloudfunctions.functions.update` without `iam.serviceAccounts.actAs` | **Excluded from privilege escalation.** Live testing with only `functions.update` + `functions.get` produced `403` even for an environment-only patch that retained the same identities. The failed update and a separate denied `iam.serviceAccounts.actAs` check are Admin Activity logs. The useful chain is already documented as `functions.update` + `actAs`; the standalone permission is not an attack technique. |
| Cloud Functions `cloudfunctions.functions.generateUploadUrl` alone | **Excluded from privilege escalation.** It creates a time-limited staging URL but cannot change or deploy a function; a later update still requires `cloudfunctions.functions.update` and `iam.serviceAccounts.actAs`. Live testing also found that the v1 audit entry falsely reports `cloudfunctions.functions.sourceCodeSet` as granted when the caller held only `generateUploadUrl`; that audit-integrity issue is retained as a private report in `$HOME/cloud_bb/gcp/cloud-functions-v1-generateuploadurl-false-authorizationinfo.md`. |
