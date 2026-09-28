# GCP audit — open frontier (next-iteration candidates)

State (2026-09-25): the authenticated technique surface is at deep saturation. Six independent
diff/scan axes run this engagement all came back exhausted beyond the 3 gaps shipped in batch 4:
service-prefix diff, individual-write-perm diff, resource-type-token diff, setIamPolicy/use/actAs
diff, credential/token-mint diff, and a fresh-catalog delta (only 21 perms added since the
session-8 dump, none attack-relevant). Remaining real gaps appear as **newly-GA/preview
sub-resources within already-documented services** — a slow trickle, not a backlog.

## 2026-09-28 boundary-day frontier — Dataplex Data Products
- [x] `CreateDataAsset` `validateOnly` securely enforced backing-resource access: a caller with
      DataAsset create but no BigQuery permissions was denied on `bigquery.datasets.get`; metadata
      plus table-IAM positive control succeeded without asset or policy mutation.
- [x] Data Product access-group principal replacement rechecked caller backing-resource authority.
      A Data Products Editor with zero BigQuery permissions received an accepted LRO, but completion
      failed on `bigquery.tables.getIamPolicy` and the table grant did not move. Failed-operation
      metadata temporarily showed the replacement principal; it had no observed privilege impact
      and was restored before full fixture deletion.

## 2026-09-28 boundary-day frontier — App Lifecycle Manager
- [x] Map the current Release/UnitOperation/Rollout actuation chain. Shipped the expected Admin
      primitive: register attacker Terraform as a new Release and apply it to an existing Unit or
      Rollout population using its prepared `actuation_sa`. Bounded the path by all actuation,
      artifact, Infrastructure Manager, UnitKind, filter and target-service prerequisites.
- [ ] In an already prepared disposable fixture, verify retained-actuation behavior under only
      Release create plus UnitOperation create, then repeat fleet mode with Rollout create. Capture
      downstream Infra Manager and target-service principals and delete the full dependency graph;
      keep any arbitrary identity-attachment discrepancy private-first. A clean low-level bootstrap
      was inconclusive: the Preview API rejected both tested global/regional reference topologies at
      its internal project-read step, despite authorizing the initiating write. Use a current App
      Design Center composite-template fixture and include the hidden ALM-created Artifact Registry
      repository in teardown.

## 2026-09-28 boundary-day frontier — API Hub plugins
- [ ] On an existing disposable API Hub instance, test `plugininstances.update` without
      `plugininstances.applyConfig` against authentication/additional-config fields, then measure
      Cloud Audit Logs for every current plugin/instance create, update, execute and delete method.
- [ ] Resolve callback identity, redirect credential forwarding and hosting-account delegation using
      only synthetic secrets and zero-role identities. Provisioning this lab is not clean because
      deprovision leaves a seven-day Apigee organization cooldown; use `api-hub/checklist.md`.

## 2026-09-28 boundary-day frontier — Storage Batch Operations dry run
- [x] Corrected the existing absolute caller-identity statement: real transforms re-check caller
      permissions, but bucket-list/manifest runtime also depends on the job-project service agent;
      project-source/CEL explicitly uses caller credentials.
- [ ] In an already-enrolled Storage Intelligence fixture, test whether `dryRun=true` exposes
      aggregate prefix count/bytes to a caller with job create/get but no Storage access while the
      service agent can read/transform the synthetic bucket. Delete the job/LRO and every fixture;
      do not consume a one-time trial solely for this test.

## 2026-09-28 boundary-day frontier — Audit Manager validation
- [x] Project-scope `EnrollResource` `validateOnly` correctly enforced caller destination authority:
      a caller with no Storage permission was denied on `storage.buckets.getIamPolicy` even while the
      service agent had object-create; caller Storage Admin was the successful control. Full evidence
      and cleanup are in `audit-manager/tested.md`.
- [ ] Repeat the deputy matrix only in an already-prepared folder/organization scope with a
      cross-project empty bucket. Do not bootstrap a real enrollment because v1 has no unenroll or
      delete-enrollment RPC. Also test multi-destination short-circuiting and request-field redaction
      using only owned synthetic buckets; keep any authorization discrepancy private-first.

## 2026-09-28 boundary-day frontier — source, scanners, media and network inspection
- [ ] In disposable Cloud Functions v1/v2 fixtures with Data Access enabled, capture
      `GenerateDownloadUrl` plus the signed Storage GET, distinguish caller versus signing-service
      attribution, then restore the audit policy and delete source, builds, images and functions.
- [ ] In an explicitly disposable Cloud Shell session, compare authorized, never-authorized and
      restarted-session token behavior without retaining a bearer token or bypassing consent. Record
      only non-secret identity/scope/lifetime evidence and remove temporary access immediately.
- [ ] With synthetic Dataflow and Storage Transfer fixtures, subtract helper reads and re-test the
      exact `actAs` boundary for replacement jobs and user-managed transfer identities. Cancel jobs,
      remove staged marker objects and grants, and do not revive the old no-`actAs` claim without a
      current reproducible result.
- [ ] Run Web Security Scanner only against a disposable same-project application at low QPS; capture
      scan/result telemetry and request-field redaction, then delete the configuration and every
      scanner-created application record. Treat any cross-target or link-local acceptance as private
      report material and never probe an unowned host.
- [ ] In synthetic Live Stream/Transcoder fixtures, measure RTMP/SRT admission, channel-activity
      logging, stream-key list/get parity and minimum service-agent object permissions. Stop billed
      channels immediately and delete inputs, assets, events, jobs, objects, buckets and grants.
- [ ] In a disposable VMware private cloud, capture credential-show/reset, private-cloud IAM,
      vCenter clone and NSX policy evidence under minimum roles. Never inspect production workloads;
      restore passwords/policies and delete clones, snapshots, rules and temporary identities.
- [ ] Capture Cloud IDS exception and DNS Threat Detector update telemetry with reversible values;
      the current audit catalog omits DNS Threat Detector, so keep its logging class unverified until
      observed. Separately validate NSI producer/consumer `.use` grant placement only with disposable
      packet-processing infrastructure and remove every endpoint, association, profile and rule.
- [ ] Recheck VPC-SC dry-run update/enforce/drop and `metadata.dryRun` with a harmless disposable
      access policy. Keep VPC-SC post-exploitation empty unless a future method itself discloses data
      or creates execution without first weakening the perimeter.

## Open, genuinely-uncovered leads deferred for lack of testable infra (verify when feasible)
- [x] **Managed Workload Identity attestation-rule persistence — RESOLVED/SHIPPED (batch 6, 2026-09-25).**
      Live-verified control plane: `workloadIdentityPoolManagedIdentities.setAttestationRules` (or
      `roles/iam.workloadIdentityPoolAdmin`, no `setIamPolicy`) enrolls an attacker workload into a
      privileged managed identity, invisible to `getIamPolicy`. Shipped to
      `gcp-workload-identity-federation-persistence.md`. Downstream token/cert mint by the attested
      workload is the only doc-grounded piece (needs a real matching GCE VM). WIF `providerKeys`
      (SAML-decrypt) + `namespaces` were dismissed as non-primitives (batch 5).
- [ ] **googleTagGatewayPolicies end-to-end** — SHIPPED from API surface (batch 4). When the resource
      reaches GA + gcloud support, live-verify the first-party-JS injection by standing up an external
      Application LB + backend + attaching a policy in the lab, and confirm an attacker GTM tagId's
      custom-HTML JS actually executes first-party. Upgrade the page's caveat if verified.
- [ ] **iam.oauthClients token-exchange** — SHIPPED persistence (attacker half live-verified). If a
      workforce identity pool + external IdP can be stood up (needs org access), live-verify the
      refresh-token capture end-to-end and quantify the phishing/consent step.

## 2026-09-28 boundary-day frontier — Build, BMS, Looker and managed file transfers
- [ ] In a purpose-built BMS environment, test standard initial-password retrieval with separate
      principals for direct Secret Manager access and customer credential-service-account
      impersonation. Separately test Preview `LoadInstanceAuthInfo` custom-role grantability and
      CMEK decrypt, `root` versus `customeradmin` local-login policy, rotation behavior and BMS/IAM
      Credentials/Secret Manager/KMS/host telemetry. Remove every local credential artifact.
- [ ] With a harmless synthetic Cloud Build, compare Cloud Logging, customer-owned bucket and
      Google-owned default-bucket reads under minimum custom roles. Capture the helper's
      `GetBuild`, confirm the customer's visibility boundary for Google's bucket, and evaluate
      approval only as part of a real source-poisoning/accepted-input chain—not as standalone
      escalation. Delete the build outputs, bucket and grants.
- [ ] In a disposable Looker (Google Cloud core) instance, capture whether `ExportInstance` emits a
      control-plane audit record, then correlate the service agent's Storage/KMS calls for non-CMEK
      and CMEK instances. Test application-query and SQL Runner permissions only with synthetic
      models and data; delete exports, credentials, grants and test content.
- [ ] On disposable Managed Lustre and Parallelstore instances, reduce the documented bucket roles
      to exact object permissions, test the caller-selected transfer-service-account attachment
      check, and capture transfer LRO plus cross-project Storage logs. Use an isolated pre-created
      directory, mount it after transfer, delete every staged file and verify no imported content,
      bucket object, binding or operation remains.

## 2026-09-28 boundary-day frontier — App/runtime delegation and service registries
- [ ] Validate App Engine `exportAppImage` only with a disposable Artifact Registry repository:
      determine the actual writer identity, exact destination permissions, cross-project behavior,
      returned image contents and both projects' telemetry, then delete the exported package and
      repository. Keep it out of the book until those material boundaries are established.
- [ ] In an organization-owned disposable project whose managed constraint already permits a test
      API, validate service-account authorization-key creation with the smallest custom roles and
      capture LRO/binding telemetry. Do not loosen organization policy or use a project where the
      key's 30-day recovery window violates cleanup requirements.
- [ ] Revalidate Binary Authorization named platform policies, attestor delegation and breakglass
      telemetry only against disposable GKE/Cloud Run workloads; restore the exact original policy,
      delete every occurrence/revision/Pod and remove only the injected public key.
- [ ] Use disposable domains and isolated Service Directory clients to capture DNSSEC/registrar
      propagation, endpoint-selection behavior and downstream DNS/network evidence. Never transfer a
      production registration, flush shared caches or repoint a namespace used by real workloads.

## 2026-09-28 boundary-day frontier — API Keys remote MCP
- [ ] The `apikeys_list_keys` two-layer authorization case is **resolved as correctly enforced**:
      `roles/mcp.toolUser` + `apikeys.keys.list` succeeded, while removing either usable layer was
      denied after endpoint-specific IAM propagation. Exact `tool.name` allow conditions and
      duplicate JSON `name` fields were also enforced consistently with no parser desync. Continue
      with the remaining tools only when a no-residue fixture is available, and test
      cross-project policy binding. `tool.isReadOnly` requires an IAM deny policy and is blocked in
      this lab because its Owner lacks deny-policy creation; retry only with that explicit authority.
      Keep results private unless a real boundary failure is found.
- [ ] Determine whether the incorrect-looking `destructiveHint:false` on `apikeys_update_key` has a
      security consequence in a Google-controlled client. The hint alone is advisory and below the
      reporting/book bar. Full matrix, constraints and official sources: `api-keys/checklist.md` and
      `api-keys/tested.md`.

## 2026-09-28 boundary-day frontier — fixed managed-service authorization patterns
- [x] Reconciled the historical cross-project page with the current 2026 bulletins and removed the
      stale public treatment of patched CVE-2026-4644 as a live Connector `actAs` bypass.
- [ ] Re-test **variations**, not the patched exact bugs: target-project authorization on every
      create/import/attach path; caller + P4SA double authorization for caller-selected secrets;
      connector/JDBC parser disagreement; internal-header stripping; cross-tenant identifiers in
      private console aggregation APIs; sandbox link-local reachability; and owner binding for
      globally named destinations. Use `cross-project-history/checklist.md`, keep a confirmed
      platform boundary failure private, and clean every fixture.

## 2026-09-28 boundary-day frontier — API Gateway MCP and data agents
- [x] Live-verified API Gateway's new OpenAPI 3.x MCP default: lifecycle methods and `tools/list`
      accepted no credential, and discovery returned exact tool names, descriptions and input
      schemas. `tools/call` inherited the deliberately unauthenticated synthetic REST operation; no
      protected-route bypass was observed. Automatic platform logs included the derived
      `McpDiscoveryService.ListMcpTools` entry. The complete no-residue fixture is recorded in
      `api-gateway/tested.md`.
- [ ] Test MCP-to-REST authorization and parser boundaries only with harmless echo/protected routes:
      duplicate tool names/arguments, type and path coercion, case-variant headers, Agent Registry
      publication/removal and attacker-written tool descriptions. Use `api-gateway/checklist.md` and
      keep an actual boundary failure private.
- [x] Tested Preview model routing with a disposable arbitrary HTTPS backend. Config validation
      accepted the backend, but runtime authentication was a Google-signed, one-hour identity JWT
      audience-bound to that exact URL—not a reusable OAuth access token. The complete no-residue
      fixture is recorded in `api-gateway/tested.md`; do not report OAuth-token exfiltration.
- [x] Rejected BigQuery data-agent default Google-managed credentials as a standalone escalation:
      Google documents one-time end-user OAuth and execution with that user's permissions. Retained
      Agent Registry/A2A identity-mix-up and editor-to-user disclosure variants as controlled test
      candidates in `bigquery/checklist.md`.
- [x] Added the distinct documented Gemini Enterprise periodic-BigQuery exposure: source BigQuery
      IAM is not propagated to the indexed copy, so an authorized app user can search fields in that
      copy without direct table permission. This is expected post-exploitation, not a bypass.

## 2026-09-28 boundary-day frontier — Resource Manager IAM v3 and tags
- [x] Added the missing PAB PolicyBinding restriction-escape chain: delete the last applicable
      project-principal-set binding or conditionally exclude a controlled principal. Exact project
      and organization permissions are required; impact is eligibility restoration only, not a new
      allow grant or deny bypass. See `resource-manager/tested.md`.
- [x] Live-captured project tag IAM and binding telemetry. Runtime TagValue IAM uses
      `TagValues.SetIamPolicy`, omits the member/role, and TagBinding create/delete emits paired
      value-side and target-side Admin Activity records. The no-condition fixture was fully removed.
- [ ] In an authorized organization-scoped fixture, capture PAB PolicyBinding update/delete LRO
      placement and project/folder moves. The current lab project has no organization authority;
      keep the official dual-resource permission bounds until such a fixture is available.

## 2026-09-28 boundary-day frontier — Deploy, messaging, workflows and DLP
- [ ] Revalidate Cloud Deploy's separate render/deploy `actAs` failures with different execution
      accounts, and correlate release/rollout, Cloud Build and runtime audit principals. See
      `cloud-deploy/checklist.md`; remove every pipeline, target, release and staged object.
- [ ] Resolve whether Pub/Sub custom BigQuery/Cloud Storage export identities can be cross-project,
      and capture the exact destination writer/audit methods. The public push-token receiver is
      normally unavailable inside VPC-SC and must not be presented as a perimeter bypass. See
      `pubsub/checklist.md`.
- [ ] Revalidate the Workflows default-account `actAs` check, source-only identity retention,
      callback discovery and `LOG_NONE` precedence with a disposable fixture. Current docs do not
      support the old omitted-identity bypass claim. See `workflows/checklist.md`.
- [ ] Capture DLP `CreateDlpJob` request fields, scheduled-trigger runtime telemetry, cross-project
      findings writes and unwrapped/KMS-wrapped re-identification under minimum custom roles. The
      current official contracts describe dangerous expected delegation, not a zero-day. See
      `dlp/checklist.md`.

## 2026-09-28 boundary-day frontier — Dataform, Network Security, reCAPTCHA and Eventarc
- [ ] Revalidate Dataform creator-role configuration and strict-act-as platform logs with a
      disposable repository. Do not restore internal commit poisoning unless product contracts
      expose an automatic compilation path without reintroducing caller `actAs`. See
      `dataform/checklist.md`.
- [ ] Validate Network Security's attached-policy, address-group and trusted intercept-deployment
      effects with minimum custom roles only when a no-residue data plane is available. Preserve
      every consuming rule/policy and remove the malicious child or membership immediately. See
      `networksecurity/checklist.md`.
- [ ] Capture reCAPTCHA propagation and platform telemetry with synthetic keys and assessments;
      separate legacy-secret possession from the Classic/no-billing quota fail-open contract. The
      Related Accounts API remains Pre-GA. See `recaptcha-enterprise/checklist.md`.
- [ ] Test whether a destination-only Eventarc pipeline update that retains its authentication
      account requires a fresh `actAs` check, and capture exact Advanced token-mint/publish audit
      placement. Keep a real attachment failure private and delete every route, token capture and
      service-agent grant. See `eventarc/checklist.md`.

## 2026-09-28 boundary-day frontier — Functions, Kafka, Metastore and SecOps
- [ ] Revalidate Cloud Functions source deployments with separate disposable runtime and build
      identities, subtracting helper permissions and capturing attachment/build telemetry. Test the
      environment-only startup-loader path only with a benign pre-existing hook. Never retain a
      bearer token, and remove functions, revisions, images, source objects, accounts and bindings.
      See `cloud-functions/checklist.md`.
- [ ] In an empty disposable Managed Kafka cluster, compare connection-authentication logging with
      Data Access off/on; test overlapping ACLs, protocol-versus-control-plane topic mutations,
      direct offset operations and the stable-versus-guide Schema Registry hard-delete contract.
      Delete the cluster, Connect resources, sink and every ACL/binding. See
      `managed-kafka/checklist.md`.
- [ ] In a disposable Dataproc Metastore service, resolve operation polling and artifact reads under
      minimum custom roles, then capture caller/service-agent Storage entries and start/completion
      LRO records for the retained primitives. Use synthetic metadata and restore URIs before full
      cleanup. See `dataproc-metastore/checklist.md`.
- [ ] In an authorized migrated Google SecOps test tenant, capture the public-versus-`v1main` method
      names and query-text audit behavior, then measure reversible reference-data, feed and synthetic
      case changes. Do not touch production telemetry or investigations. See
      `google-secops/checklist.md`.

## 2026-09-28 boundary-day frontier — Bigtable, Dataplex, Apigee and Document AI
- [ ] With a disposable Bigtable logical view, live-confirm whether a direct resource-level IAM
      grant is honored for downstream reads. Also capture source/destination restore audit placement,
      CMEK behavior and helper-versus-raw IAM permission differences. Remove every view, table,
      backup, binding and temporary key grant. See `bigtable/checklist.md`.
- [ ] In a disposable Dataplex lake, separate task creation from execution-account behavior and
      capture backing Storage/BigQuery access. Validate managed data-role propagation and policy-tag
      enforcement only with synthetic data, then remove the task, assets and bindings. See
      `dataplex/checklist.md`.
- [ ] Revalidate Apigee proxy/shared-flow dual-permission checks, service-account attachment and
      resource-level policy behavior only if an existing disposable organization is available; do
      not provision a paid organization for the test. Audit Archive deployment separately and keep
      KVM/debug/developer-key reads in post-exploitation. See `apigee/checklist.md`.
- [ ] With disposable processors and synthetic documents, capture Document AI dataset-read and
      processor-version-import logs under minimum custom roles. Test same-region and VPC-SC
      prerequisites without copying customer documents, then remove processors, versions and P4SA
      grants. See `document-ai/checklist.md`.

## 2026-09-28 boundary-day frontier — Dataflow, DMS, Billing and Service Usage
- [ ] Revalidate Dataflow's selected-worker execution with an existing staging bucket and a harmless
      metadata-email proof, then separately replace and restore a generation-unpinned synthetic UDF.
      Capture caller, worker, Storage and Compute telemetry and remove every job, object generation,
      bucket, identity and binding. See `dataflow/checklist.md`.
- [ ] Resolve the DMS Cloud SQL destination-profile permission conflict only in an already-enabled
      disposable project that can be deleted. Use an inert TEST-NET source profile, a principal with
      the four enumerated DMS/Service Usage permissions and no `cloudsql.*`, capture the output-only
      `cloudsql.cloudSqlId`, and delete both the profile and any label-discovered partial instance.
      Do not enable DMS in the shared lab merely for this test. See `database-migration/checklist.md`.
- [ ] With a disposable billing account or explicitly authorized equivalent, capture billing-account
      `GetIamPolicy`, `SetIamPolicy`, project association and payment-setting evidence under the
      minimum split permissions. Restore the complete IAM policy and association immediately; do not
      alter a real payment method. See `billing/checklist.md`.
- [ ] Recheck hierarchical Service Usage consumer-policy helper behavior and legacy-versus-Cloud-
      Quotas telemetry only with reversible synthetic state. Continue monitoring the deprecated MCP
      and content-security discovery resources, but do not claim Model Armor bypass while authorized
      reads return `SU_MCP_DEPRECATED`. See `service-usage/checklist.md`.

## 2026-09-28 boundary-day frontier — Scheduler, Spanner, Source Repositories and Runtime Config
- [ ] Revalidate Scheduler's HTTP identity attachment with separate OAuth- and OIDC-compatible
      synthetic receivers, then capture job mutation, forced-run and delivery logs. Exercise the
      App Engine and Pub/Sub paths only against inert same-project handlers/topics, and delete every
      job immediately. See `cloud-scheduler/checklist.md`.
- [ ] In a disposable Spanner environment, split caller permissions across source and destination
      principals to validate copy/restore authorization, CMEK service-agent checks and exact LRO log
      placement. Separately test FGAC role expansion with a minimal custom IAM role. Remove every
      backup, restored database, binding and temporary key grant. See `spanner/checklist.md`.
- [ ] For an eligible existing Cloud Source Repositories organization, validate a synthetic
      unapproved trigger branch and private clone under minimal custom roles. Capture `ReceivePack`,
      `LsRemote`, `UploadPack`, build and policy telemetry, then restore refs and IAM and delete all
      fixtures. Do not provision a new dependency on this closed-to-new-customers service. See
      `source-repositories/checklist.md`.
- [ ] Continue monitoring the standalone Runtime Config API after Deployment Manager support and
      shutdown milestones. If a disposable already-enabled project remains available, repeat the
      read and policy fixture with Data Access explicitly enabled to distinguish unsupported audit
      integration from project configuration. Restore the exact config policy and delete every
      variable, waiter and config. See `runtimeconfig/checklist.md`.

## 2026-09-28 boundary-day frontier — Analytics Hub, CA Service, Data Fusion and Deployment Manager
- [ ] Resolve Analytics Hub's official `SubscribeListing` audit contradiction with a disposable
      listing and subscriber project: capture the method, service-agent access, linked dataset or
      Pub/Sub subscription creation, and downstream BigQuery/Pub/Sub use. Test clean-room analysis
      rules with synthetic rows only, remove every subscription/listing/exchange and restore IAM.
      See `analytics-hub/checklist.md`.
- [ ] With a disposable CA pool, validate raw-certificate issuance without helper-only reads,
      template-constraint relaxation, template IAM audit placement and subordinate-CA signing with
      a cross-project key. Use only synthetic identities, restore the exact pool/template policies
      and constraints, and delete every certificate, CA, pool, key grant and temporary key. See
      `certificate-authority-service/checklist.md`.
- [ ] In a disposable Data Fusion instance, separate caller, design-time service account, pipeline
      VM account and service agent under minimum custom roles. Capture pipeline, Preview and
      namespace-IAM telemetry—especially the currently undocumented namespace policy class and
      default—and remove every pipeline, namespace, account, binding and instance. See
      `data-fusion/checklist.md`.
- [x] Live-proved that deployment-level `roles/deploymentmanager.admin` authorizes an otherwise
      unprivileged principal to read that exact existing deployment. The binding did not provide
      project-level list/create; the direct policy was restored and every fixture plus API state was
      removed/restored. See `deployment-manager/tested.md`.
- [ ] Before Deployment Manager's June 30, 2027 shutdown, use a harmless synthetic deployment to
      capture create/update deputy behavior under a minimum caller role and a deliberately bounded
      Google APIs Service Agent. Separately test manifest redaction shapes and type-provider request
      boundaries without targeting metadata or private services. Restore the service-agent policy,
      delete every deployment/bucket/account and return the API to its original state. See
      `deployment-manager/checklist.md`.

## 2026-09-28 boundary-day frontier — BeyondCorp, BigLake, Container Analysis and VM Migration
- [ ] With an existing disposable licensed Security Gateway, capture current gateway/application
      IAM method names and defaults, then test same-VPC endpoint repointing and the undocumented
      server-side handling of an `upstreams` update. Restore the exact etag-protected policy and
      route; do not claim cross-VPC routing until it succeeds. See `beyondcorp/checklist.md`.
- [ ] In a disposable Lakehouse catalog, call stable v1 `/credentials` under isolated
      `getData`/`updateData` custom roles, capture whether the omitted stable
      `LoadIcebergTableCredentials` method emits a log, and correlate scoped Storage use with the
      final Iceberg commit. Never retain the returned token and delete every catalog, object,
      binding and managed identity that can be removed. See `biglake/checklist.md`.
- [ ] In synthetic Container Analysis projects, split occurrence creation from note attachment,
      validate bad and correctly signed attestations, and remove each cross-project attestor/note
      service-agent grant in turn. Resolve the current `UpdatePolicy` permission/catalog mismatch,
      restore complete policies with etag protection and delete every occurrence, note, attestor and
      key. See `container-analysis/checklist.md`.
- [ ] In disposable VM Migration host/target projects, separate the raw migrating-VM update,
      caller-console `actAs`, host P4SA `actAs`, explicitly selected runtime account and clone.
      Capture LRO and downstream Compute/Storage/AWS evidence for synthetic metadata, image import
      and Preview disk migration, then delete every clone, image, disk, snapshot and binding. See
      `vm-migration/checklist.md`.

## 2026-09-28 boundary-day frontier — Cloud Identity, Developer Connect, Advisory Notifications and Healthcare
- [ ] In a disposable licensed Workspace tenant, capture regular, security, dynamic and locked-group
      membership authorization under default and customized `whoCanModerateMembers`, then correlate
      Groups/Enterprise Groups events with optional Cloud Logging sharing. Exercise only synthetic
      IAM bindings and remove every membership, setting and binding. See `cloud-identity/checklist.md`.
- [ ] With two disposable Workspace/GCP tenants, test the bounded DWD cross-organization client-ID
      inference and Access Evaluation attribution using a narrow read-only scope. Revoke the DWD
      grant, key/signing authority and every test account immediately. See `cloud-identity/checklist.md`.
- [ ] In a disposable provider repository, compare raw read/read-write token roles, the system Git
      proxy and self-scoped account-connector token under minimum roles. Capture exact provider and
      GCP telemetry, respect protected refs and remove links, connections, grants and test commits.
      See `developer-connect/checklist.md`.
- [ ] Derive the Preview generic HTTP proxy request contract only against a controlled endpoint,
      then verify caller-plus-P4SA authorization for cross-project secrets and header/path bounds.
      Keep any real authorization failure private and delete every secret, connection and grant. See
      `developer-connect/checklist.md`.
- [ ] Retry Advisory Notifications only in an already-operational disposable organization with
      synthetic state. Compare BASIC/FULL reads, capture the stable-v1 update method, preserve the
      complete settings map and current etag, and restore only the controlled optional setting. Do
      not alter mandatory notices, real Essential Contacts or production SOC delivery. See
      `advisory-notifications/checklist.md`.
- [ ] In isolated no-PHI Healthcare stores, capture stable-v1 start/end LRO logs, caller/P4SA Storage
      and BigQuery access, continuous-streaming telemetry and consent behavior under minimum custom
      roles. Snapshot full store configuration/IAM first; remove every stream, notification, grant,
      sink and synthetic resource and verify no LRO or delivery remains. See `healthcare/checklist.md`.

## 2026-09-28 boundary-day frontier — Federation, OS Config, Contact Center Insights and AlloyDB
- [ ] In disposable federation fixtures, capture OIDC static-JWKS workload takeover and workforce
      programmatic exchange while proving the workforce Console-sign-in limitation. Separately
      validate managed-identity X.509 issuance against a controlled mTLS relying workload. Account
      for 30-day tombstones and remove every binding, workload and revivable trust object. See
      `workload-identity-federation/checklist.md`.
- [ ] On disposable Linux and Windows VMs, validate patch object-read/scope boundaries, GA and
      legacy inline policy execution, assignment-update-only authority and standard versus custom
      agent identities. Use a preconfigured disposable hierarchy for orchestrator tests; restore
      policies, service-agent grants, feature settings and audit settings, then delete all guests
      and artifacts. See `osconfig/checklist.md`.
- [ ] In a synthetic Contact Center Insights project, capture signed-audio, supported-format GCS
      import and cross-project BigQuery export with isolated caller/P4SA permissions. Resolve the
      `conversations.list` versus unused-looking `.export` permission boundary and delete every
      conversation, object, table, dataset and temporary grant. See
      `contact-center-insights/checklist.md`.
- [ ] In a disposable AlloyDB cluster, isolate Viewer-level export, built-in versus IAM user roles,
      Data API/Studio/MCP database authorization, and cross-project backup restore source checks.
      A missing source authorization is private-report material. Delete all users, objects, exports,
      restored resources, network paths and grants, and return any initially disabled API to
      disabled. See `alloydb/checklist.md`.

## 2026-09-28 boundary-day frontier — live correction and newly launched surfaces
- [x] Dialogflow CX configured-service-account webhook authorization: external and Cloud Run
      receivers were rejected, a Google-API URI-only update without `actAs` failed, and the authorized
      control succeeded. The provisional token-capture page was removed and cleanup verified. See
      `dialogflow/tested.md`.
- [ ] Test Preview managed workload identity on global/regional load-balancer backend services. A
      backend creator can select immutable `tlsSettings.identity`, while current docs expose no
      `actAs`-style permission. Use a wildcard-free synthetic attestation rule and controlled mTLS
      server; private-report any cross-identity use, then delete the backend, trust resources, certs,
      network and grants.
- [x] Closed Workbench/Colab schedule retained-identity update as unsupported and documented gated.
      Legacy schedules have no PATCH; current clients treat the notebook execution request as
      immutable, and Google requires the named user or service-account actAs for schedule changes.
      VM-local user ADC is not a Schedule field. See `workbench/tested.md`.
- [x] Live-verified SQL Server `sp_help_revlogin` password-hash/SID export, published the bounded
      expected post-exploitation technique, disabled the flag, and deleted both test fixtures and
      local clients. Exact same-subject Workforce Identity crossover is a documented limitation;
      keep only case/domain/length/Unicode/delimiter normalization variants open for a private-first
      two-principal test. See `cloud-sql/tested.md` and `cloud-sql/checklist.md`.
- [ ] Re-run the CES OpenAPI-tool retained-service-account partial-update test only in a project with
      explicit CES write access. The current Owner control had `ces.apps.create` granted but the
      product separately denied project write access, so no app/tool or boundary result exists.
      Keep missing actAs private-first and use Google `userinfo` instead of an external token
      receiver. See `ces/tested.md` and `ces/checklist.md`.
- [ ] Test Backup and DR Preview auto-protection with same-organization disposable projects to bound
      policy/binding authorization versus later restore authority. Remove policies, bindings,
      backups, vault, operator grants and synthetic workloads after all LROs settle.
- [x] Cloud Scheduler's partial-update arm is securely resolved: after an unauthenticated canary
      proved `jobs.update` propagation, a raw URI-only authenticated-job PATCH was denied on retained
      service-account `actAs`; the identical authorized control succeeded and preserved identity and
      audience. Cleanup restored the baseline. Continue the separate private-first Eventarc pipeline
      check; never publish a missing recheck before coordinated disclosure, and delete every route,
      token, receiver and SA.
- [ ] In a disposable Firebase App Hosting backend, verify whether image-source Build plus Rollout
      alone executes under the existing backend identity without caller `actAs`; capture App Hosting,
      Cloud Build and Cloud Run principals and delete the rollout/build/image afterwards. See
      `firebase-app-hosting/checklist.md`.
- [ ] In an isolated fleet, publish one namespaced Config Delivery manifest and capture the exact
      Config Delivery, Config Sync and Kubernetes principals/methods, then remove the fleet package,
      release and bundle and verify propagated objects are gone. See `config-delivery/checklist.md`.
- [ ] In disposable Filestore and Backup for GKE fixtures, validate minimum custom roles, LRO helper
      permissions and protocol/PV restore behavior. Unmount clients and delete every clone, backup,
      restore, cluster, firewall rule and temporary grant after verification. See
      `filestore/checklist.md` and `backup-dr/checklist.md`.
- [ ] Capture exact producer audit method names for a benign Service Catalog version patch and the
      exact source-IAM/finding methods for SCC v2 with Data Access logging enabled. Restore the
      original version/policy and remove every temporary binding. See `private-catalog/checklist.md`
      and `security-command-center/checklist.md`.
- [ ] Retest Data Fusion secure-store access with a least-privilege token to resolve the RBAC guide's
      `getSecret` statement against the current audit catalog's narrower authorization row. Use only
      a synthetic secret, then delete it and every temporary grant. See `data-fusion/checklist.md`.

## Monitoring cadence (the productive vein)
- [ ] Periodically re-pull `gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/<lab>`
      (needs `gcloud config set billing/quota_project <lab>`), diff vs the prior dump, and triage any
      NEW service prefixes / resource-type tokens for attack primitives. Current baseline dump:
      **13,701 permissions, reconfirmed unchanged 2026-09-28** (batch 5 was +3 vs 13,698;
      AI/analytics/preview noise, none attack-relevant).
- [ ] Watch newly-GA GCP features (release notes) for identity/traffic/exec/exfil surfaces; those are
      where the next real gaps will be (this iteration's 3 were all GA-2024/preview resources).

## Assessed and intentionally NOT authored (no-garbage bar)
- **(batch 7, 2026-09-25)** iamconnectors.retrieveCredentials (= Agent Identity, documented),
  dataprocrm.nodes.mintOAuthToken (internal node protocol), cloudsql.createTestingAgentSession
  (admin-only / Gemini agent), aiplatform.sandboxEnvironments/extensions/sessions execute
  (Google-managed identity, no project SA), firebaseauth.createSession / firebasedataconnect
  impersonate (documented in Firebase pages), confidentialcomputing.challenges (TEE-gated, not
  cost-light, attestation-0day if abusable), networkmanagement.generateProviderAccessToken /
  developerconnect.generateGitHubStateToken (niche/non-credential). All ruled out — see STATUS batch 7.
- compute.instantSnapshots — same disk-exfil family; annotated as a NOTE, not a technique.
- compute.regionSslPolicies.setIamPolicy, dataplex.entryLinkTypes.* — generic self-grant / catalog
  metadata; no distinct primitive.
- fpnv.phoneNumberTokens.* — telco/payments test tokens, not a GCP-access primitive.
- KMS kajPolicyConfigs, GKE Backup channels, Storage Insights, Developer Connect, NSI
  mirroring/intercept deployment groups — all covered-concept or documented elsewhere.

## Documentation-quality backlog: per-technique stealth
- [ ] Complete the explicit stealth rating on every genuine privesc and post-exploitation technique.
      The deterministic `scripts/check_gcp_technique_metadata.mjs` scan after the BigQuery, Compute,
      Vertex AI and IAM batch finds **140 unrated** qualifying sections: 246/287 privesc and 245/344
      post-exploitation H3 blocks that already contain exact `Potential Impact` and `Logs generated`
      markers also have an exact `Stealth` marker. Persistence is 153/153. These figures supersede
      the former manual baseline, which could not be reproduced against its own published commit.
      Secret Manager,
      Cloud Tasks, Parameter Manager, Secure Source Manager, Cloud
      Run, IAP, Cloud KMS, Dataproc privesc, GKE privesc, Security Command Center and Cloud
      Logging post-exploitation, Cloud Storage post-exploitation, Firebase privesc, Monitoring and
      Cloud DNS post-exploitation, Integration Connectors, Cloud Build privesc, Cloud SQL and
      Discovery Engine, Bigtable and Artifact Registry post-exploitation, Cloud Storage, Artifact
      Registry, App Engine, Composer, Resource Manager, Cloud Deploy, Pub/Sub and Workflows privesc,
      Sensitive Data Protection post-exploitation and persistence, Dataform and Network Security
      privesc, reCAPTCHA Enterprise post-exploitation, Eventarc privesc/post-exploitation/persistence,
      Cloud Functions privesc, Managed Kafka, Dataproc Metastore and Google SecOps post-exploitation,
      Bigtable, Dataplex, Apigee, Dataflow, Cloud Billing, Cloud Scheduler, Spanner, Cloud Source
      Repositories, Runtime Config, Analytics Hub, Certificate Authority Service, Data Fusion and
      Deployment Manager privesc, Document AI, Cloud Source Repositories, Runtime Config and
      Deployment Manager post-exploitation, Certificate Authority Service persistence, Database
      Migration Service and Service Usage zero-H3 audits, BeyondCorp, BigLake/Lakehouse, Container
      Analysis and VM Migration privesc/post-exploitation, BeyondCorp, BigLake/Lakehouse and
      Container Analysis persistence, VM Migration zero-H3 persistence, Cloud Identity,
      Developer Connect, Advisory Notifications and Healthcare privesc/post-exploitation,
      Cloud Identity and Healthcare persistence, Google Groups and Healthcare unauthenticated
      access, API Gateway unauthenticated techniques, Workload/Workforce Identity Federation,
      OS Config, Contact Center Insights, AlloyDB, BigQuery, Compute Engine, Vertex AI and IAM have
      been handled.
- [ ] Review ratings against the service's current audit reference and any downstream service/platform logs; do not classify solely by whether the primary API call is logged. Record corrections in each service's `tested.md`, then update PR #414 in small batches.
