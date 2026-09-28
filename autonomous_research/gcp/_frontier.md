# GCP audit — open frontier (next-iteration candidates)

State (2026-09-25): the authenticated technique surface is at deep saturation. Six independent
diff/scan axes run this engagement all came back exhausted beyond the 3 gaps shipped in batch 4:
service-prefix diff, individual-write-perm diff, resource-type-token diff, setIamPolicy/use/actAs
diff, credential/token-mint diff, and a fresh-catalog delta (only 21 perms added since the
session-8 dump, none attack-relevant). Remaining real gaps appear as **newly-GA/preview
sub-resources within already-documented services** — a slow trickle, not a backlog.

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
      A fresh reproducible 2026-09-28 scan after the Cloud Deploy, Pub/Sub, Workflows and Sensitive
      Data Protection batch finds **312 unrated** qualifying sections: 170/311 privesc and 193/364
      post-exploitation H3 blocks that already contain Potential Impact and `Logs generated` also
      have an explicit Stealth rating. Persistence is 154/154 under the same scan. Secret Manager,
      Cloud Tasks, Parameter Manager, Secure Source Manager, Cloud
      Run, IAP, Cloud KMS, Dataproc privesc, Compute privesc and post-exploitation, GKE privesc,
      BigQuery privesc and post-exploitation, Vertex AI privesc, Security Command Center and Cloud
      Logging post-exploitation, Cloud Storage post-exploitation, Firebase privesc, Monitoring and
      Cloud DNS post-exploitation, Integration Connectors, IAM and Cloud Build privesc, Cloud SQL and
      Discovery Engine, Bigtable and Artifact Registry post-exploitation, Cloud Storage, Artifact
      Registry, App Engine, Composer, Resource Manager, Cloud Deploy, Pub/Sub and Workflows privesc,
      Sensitive Data Protection post-exploitation and persistence, and API Gateway unauthenticated
      techniques have been handled.
- [ ] Review ratings against the service's current audit reference and any downstream service/platform logs; do not classify solely by whether the primary API call is logged. Record corrections in each service's `tested.md`, then update PR #414 in small batches.
