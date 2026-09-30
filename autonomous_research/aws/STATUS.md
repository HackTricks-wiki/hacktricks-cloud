# AWS audit — status

Last updated: 2026-09-30

## Active 2026-09-27 checkpoint

Research remains active on branch `research/aws-technique-audit` and PR #413. The current sweep added or substantially refreshed public enumeration and attack coverage for Customer Profiles, Invoicing and Billing, Resource Explorer 2, User Notifications, Payment Cryptography, Supply Chain, Verified Permissions, Clean Rooms/Clean Rooms ML, WorkSpaces Web, Billing Data Exports, Network Manager/Cloud WAN, End User Messaging Social, AppFabric, Mainframe Modernization, and Migration Hub Refactor Spaces, WorkSpaces Thin Client, Migration Hub Orchestrator, AppIntegrations, Application Discovery Service, core Migration Hub, Migration Hub Strategy Recommendations, MemoryDB, and Resilience Hub (including the September 2026 next-generation API), Glue, Redshift/Redshift Serverless, S3 Tables, S3 Vectors, Backup Search, Entity Resolution, Timestream, and Bedrock Data Automation, Systems Manager GUI Connect, Billing Conductor, License Manager, WorkMail Message Flow, the separate Amazon Connect voice Contact Lens transcript API, and the WorkSpaces Instances AMI/user-data/instance-profile launch path, plus Lambda durable-execution history disclosure and callback result injection and CloudWatch Observability Admin telemetry-pipeline anti-forensics. The latest live Amplify branch test also proved that exact-branch `UpdateBranch` environment-variable control plus `StartJob` can activate a repository-local runtime hook and access AWS resources as the app's existing service role, without caller-side `iam:PassRole` or downstream access. Amplify `CreateWebHook` was also verified as exact-branch, credential-less trigger persistence: an unsigned URL created a build job after the creating IAM user and key were deleted. New AWS PCS coverage maps the cluster, queue and compute-group attack surface and documents theft of the shared Slurm authentication key or REST JWT signing key through `GetCluster` plus an independently authorized Secrets Manager read. Amazon Connect coverage now includes `CreateParticipant` as the control-plane-to-bearer bridge for adding a custom chat bot or WebRTC customer to a known active contact without a Connect user login. Amazon EVS coverage now maps environment/host/VLAN/connector exposure and the separate IAM gates for recovering EVS-managed VCF, ESX root and connector appliance credentials from Secrets Manager. SageMaker HyperPod coverage now includes the cluster-only `UpdateClusterSoftware` custom-AMI path: it replaces node root volumes and can run as the existing instance-group role without caller-side `iam:PassRole`, subject to same-account image and orchestrator constraints. Every published technique includes its minimum permissions and prerequisites, impact or persistence scope, stealth assessment, and a compact logs-generated table. Per-service ledgers record successful and negative live branches, authorization boundaries, telemetry, and final cleanup evidence.

Unexpected security-impact findings are not published in this repository. Confirmed candidates from this sweep are documented only in the restricted local AWS report directory for separate disclosure.

Cleanup exception currently being monitored: one HealthImaging image-set version remains in an AWS-controlled `LOCKED / UPDATING` transition after its accepted revert. Its datastore cannot be deleted until that transition completes. The automated delete trap is healthy and all supporting test buckets and roles are already absent. Do not mark this audit fully cleaned until both the exact image set and datastore are confirmed absent.

The Application Auto Scaling custom-resource signed-request candidate is now closed: the exact AWS reference URL shape reached the current integration, but registration-only access was rejected by the documented caller-side validation for API Gateway GET/PATCH and CloudWatch permissions. All owned endpoint and service-linked-role fixtures were deleted.

CodeGuru Security is closed as a reasoned exclusion: the live scan API now returns the service's post-retirement `FeatureNoLongerAvailableException`; only inert default configuration and zero metrics remain readable. No public page was added and no state was changed.

Current next check: continue the missing-service/action sweep, prioritizing services with cross-account resource policies, credential/data export, stored service roles, mutable execution configuration, and unauthenticated identifiers. Re-test older exclusions when service capabilities or SDK models have materially changed.

## cont.118 (2026-09-30) — AppStream AgentAccess MCP headless desktop control

- SHIPPED #98 (end-to-end): exact-stack `appstream:UpdateStack` enabled vision, computer input,
  forwarded MCP tools, and `UserControlMode=DISABLED`; converting an ordinary stack required
  deleting incompatible user and streaming-experience settings in the same call.
- A separate operator with only exact stack+fleet `CreateStreamingURL` and stack-conditioned
  `agentaccess-mcp:InvokeMcp`, `CheckConnectionStatus`, and `GetScreenshot` initialized a real
  session and received a JPEG desktop screenshot. It had no Describe, input-tool, or PassRole
  permission; the bearer URL and screenshot content were never printed or stored.
- Published the conditional machine-role impact honestly: headless screen/input control exposes
  the session, but AWS privilege escalation still needs a usable shell/application surface and an
  existing fleet role. Forwarding exposes only MCP tools already configured in the image.
- CloudTrail retained the full agent configuration in the default `UpdateStack` event and redacted
  user/session/URL fields in `CreateStreamingURL`. Agent tool calls are optional CloudTrail data
  events; CloudWatch provides operational metrics.
- The session was explicitly expired. The one-instance On-Demand fleet reached STOPPED and was
  disassociated/deleted; the stack and temporary documented AppStream service role were deleted.
  Independent inventories found zero matching stacks, fleets, AppStream ENIs, or AppStream roles.
  Expected functionality; no AWS report.

## cont.117 (2026-09-30) — AppStream stack transfer-control weakening

- SHIPPED #97: exact-stack `appstream:UpdateStack` enabled clipboard copy in both directions, file
  upload/download, and local printing without Describe, fleet mutation, session, or caller-side
  PassRole permissions.
- The resulting stack can permit ingress and exfiltration for existing/future sessions, including
  file-system redirection when upload and download are both enabled. It does not create a session
  or bypass independent endpoint, network, EDR, or DLP controls.
- The restricted caller succeeded only for the exact stack ARN; an authorization policy naming a
  different stack was denied. The tested clipboard maximum was the documented 20 MiB.
- CloudTrail recorded the default management write after propagation and retained the complete
  settings and limits in both request and response. Streaming-channel transfers are not separate
  AppStream control-plane API events.
- The disposable stack was deleted by the test trap; an independent final inventory found zero
  matching stacks. No fleet, session, application, URL, role, bucket, or network fixture was
  created. Expected functionality; no AWS report.

## cont.116 (2026-09-30) — AppStream rolling fleet-image takeover

- SHIPPED #96 (conditional attacker image): exact-fleet `appstream:UpdateFleet` changed a stopped
  On-Demand fleet between AWS-owned Windows Server 2022 images while preserving its existing
  machine role without Describe or caller-side PassRole.
- For a running same-OS fleet, documented behavior rolls new/replacement instances onto the new
  image without interrupting active sessions. An attacker-controlled same-account or fleet-shared
  image can therefore persist code and conditionally inherit the fleet role.
- The AWS-owned public-image branch required only the exact fleet ARN. The public technique
  conservatively includes exact target-image authorization for customer-owned/shared targets, as
  exposed by the service-authorization model; that target class was unavailable live.
- CloudTrail retained the target image ARN and returned the full resulting fleet, including the
  unchanged role, state, type and zero capacity.
- The fleet stayed at desired/running capacity zero and was never started. It and both disposable
  roles were deleted; final fleet/AppStream-ENI inventories were zero. Expected functionality; no
  AWS report.

## cont.115 (2026-09-30) — AppStream Elastic-fleet SYSTEM session-script persistence

- SHIPPED #95: exact-fleet `appstream:UpdateFleet` plus exact-object `s3:GetObject` set an Elastic
  fleet's session-script archive while preserving its existing machine role without caller-side
  PassRole.
- A valid ZIP can run session-start/termination hooks as local SYSTEM or the streaming user. This is
  fleet-level recurring persistence and conditionally recovers the retained
  `appstream_machine_role` whenever later user sessions trigger it.
- The exact fleet alone failed the S3 object-access check. Adding only exact-object GetObject
  succeeded; `DescribeFleets` and a different fleet ARN were denied. No session was started.
- CloudTrail retained the exact bucket/key and returned the full fleet, including role, VPC,
  platform and capacity. Optional S3 data events and session-script output logs provide additional
  evidence, but payload configuration can disable the latter.
- The stopped Elastic fleet, placeholder object/bucket, harmless machine role, and temporary
  AppStream service role were deleted. Final checks found zero matching fleets or AppStream ENIs,
  and the bucket/roles were absent. Expected functionality; no AWS report.

## cont.114 (2026-09-30) — AppStream Elastic-application launch poisoning

- SHIPPED #94: exact-application `appstream:UpdateApplication` replaced an enabled Windows
  application's launch path with PowerShell and stored attacker-controlled arguments. No Describe,
  S3, fleet/app-block mutation, or caller-side PassRole permission was present.
- This is user-triggered, durable code execution for an already associated Elastic-fleet
  application. It can expose mapped user data, fleet network access, and an existing
  `appstream_machine_role`; separate `CreateStreamingURL` access provides a self-trigger.
- Exact boundary: only the application ARN was required for launch fields. A different application
  and app-block-only policy were denied. Supplying `AppBlockArn` required both exact resources.
- CloudTrail recorded the full executable path and launch arguments in the request and returned the
  complete resulting application definition, giving defenders a high-fidelity detection point.
- Two disposable applications/app blocks and their six harmless S3 objects were deleted. Both
  exact buckets were absent and final matching application/app-block inventories were zero. No
  fleet, stack, URL, session, machine role, instance, or network resource was created. Expected
  functionality; no AWS report.

## cont.113 (2026-09-30) — AppStream existing app-block-builder takeover

- SHIPPED #93: exact-builder `appstream:CreateAppBlockBuilderStreamingURL` creates a bearer URL to
  an existing running app-package builder without Describe, create/update, association, or
  caller-side PassRole permissions.
- The administrative Windows desktop can access the builder's existing `appstream_machine_role`.
  When an APPSTREAM2 app block is associated, finishing a malicious package also creates a
  conditional Elastic-fleet software-supply-chain path.
- Live exact-resource proof reached builder-not-found only for the allowed ARN; another builder and
  `DescribeAppBlockBuilders` were denied. A disposable associated builder then returned a real
  60-second URL, which was never printed or redeemed.
- CloudTrail recorded the successful call as a default management write, retained builder name and
  validity, and replaced the returned URL with `HIDDEN_DUE_TO_SECURITY_REASONS`.
- The builder was stopped, disassociated, and deleted. The app block, empty package bucket, and
  temporary service role were deleted. Final inventories showed zero matching builders, app
  blocks, associations, AppStream ENIs, bucket, or role. Expected functionality; no AWS report.

## cont.112 (2026-09-30) — AppStream existing image-builder administrator URL

- SHIPPED #92: exact-builder `appstream:CreateImageBuilderStreamingURL` gives direct access to an
  existing running builder without create/update, Describe, or caller-side PassRole permissions.
- Non-domain-joined Windows builders offer local Administrator; Linux automatically uses a root
  `ImageBuilderAdmin` session. This exposes the golden-image filesystem/private network and any
  existing `appstream_machine_role` credentials.
- Domain-joined Windows credentials and configured streaming access endpoints are explicit
  constraints; the public technique does not present every builder as automatically reachable.
- Live least-privilege proof reached builder-not-found on one exact ARN; another builder and
  `DescribeImageBuilders` were denied. The account had zero image builders.
- CloudTrail recorded the call as a management write, retained builder name/validity, and replaced
  the returned URL with `HIDDEN_DUE_TO_SECURITY_REASONS`.
- No builder, image, URL, session, role, network resource, or other asset was created. Expected
  functionality only; no AWS report.

## cont.111 (2026-09-30) — AppStream existing-fleet streaming URL

- SHIPPED #91: exact stack+fleet `appstream:CreateStreamingURL` creates a custom-user bearer session
  into an existing fleet without user-pool/SAML setup, fleet mutation, or caller-side PassRole.
- The URL can last seven days. A Desktop/shell-capable session inherits private-network/application
  access and can recover the fleet's existing `appstream_machine_role` credentials; tightly locked
  application-only fleets limit that escalation path.
- Live least-privilege proof reached stack-not-found with only the exact two resource ARNs. Either
  alternate resource and `DescribeStacks` were denied; the account had zero fleets/stacks.
- CloudTrail recorded a management write, retained stack/fleet/application/validity, and redacted
  the custom user, session context, and returned URL as `HIDDEN_DUE_TO_SECURITY_REASONS`.
- No fleet, stack, user, URL, session, role, or other resource was created. Expected functionality
  only; no AWS report.

## cont.110 (2026-09-30) — AppStream image export to EC2 AMI

- SHIPPED #90: `appstream:CreateExportImageTask` plus `iam:PassRole` materializes an owned private
  WorkSpaces Applications image as a same-account EC2 AMI for normal launch/copy/share inspection.
- The current export is limited to available Windows Server 2022/2025 images and strips the service
  agent plus Microsoft license-included applications. The AMI is not automatically public or
  cross-account, so separate EC2 authority remains necessary.
- Live minimum proof showed the action alone stops at PassRole; exact-role PassRole with
  `iam:PassedToService=appstream.amazonaws.com` reached image-not-found without List/Describe.
- An exact image ARN did not authorize the action, while the Region/account `image/*` pseudo-resource
  did. This useful scoping/documentation nuance was recorded but is not an AWS vulnerability.
- CloudTrail retained image name, AMI name, and role ARN for the service-authorized failed call and
  classified it as a management write. Private/shared image, export-task, and matching AMI
  inventories remained empty; no role, task, AMI, snapshot, instance, or other resource was created.

## cont.109 (2026-09-30) — AppStream private-image cross-account copying

- SHIPPED #89: exact-image `appstream:UpdateImagePermissions` can grant a foreign account fleet use
  or image-builder use of a private AppStream / WorkSpaces Applications golden image.
- The image-builder branch lets the recipient obtain local-admin/root access and create an
  independent image that survives owner-side revocation; the impact is durable disclosure of
  proprietary applications, internal configuration, cached data, and accidentally baked secrets.
- A live inline STS policy proved exact image-ARN scoping: the allowed synthetic image reached
  resource-not-found, while a different image and `DescribeImages` were denied.
- CloudTrail recorded the permitted failed probes as management writes and retained the image name,
  recipient account, `allowFleet`, and `allowImageBuilder`. It represented the service's specific
  failures as generic `UnknownError`, so detection should inspect the request fields.
- Both private and shared image inventories were empty. Only impossible image names were used; no
  image, permission, builder, fleet, IAM role, or billable resource was created. Expected
  functionality only; no AWS report.

## cont.102 (2026-09-30) — Marketplace Discovery private-offer reads

- SHIPPED #84: the April 2026 Marketplace Discovery API can enumerate buyer-visible private offers
  and offer sets, then disclose pricing, payment/renewal structure, custom legal-document URLs,
  buyer notes and replacement-agreement relationships before agreement acceptance.
- Verified the exact minimum for `ListPurchaseOptions` on the catalog purchase-option wildcard and
  exact-offer `GetOfferTerms`; the same constrained role was denied unrelated `SearchListings`.
- CloudTrail recorded every read under `discovery-marketplace.amazonaws.com`, retained the private
  visibility/product filter or exact IDs, and omitted returned terms and presigned URLs.
- The account had zero private purchase options. Public-offer reads validated all response classes
  without subscribing, purchasing, deploying, or redeeming legal-document URLs. The temporary IAM
  role and inline policy were deleted and independently verified absent. No AWS defect was found.

## cont.103 (2026-09-30) — Chime SDK technique metadata completion

- Added explicit minimum-permission/prerequisite blocks to every executable Chime SDK privilege
  escalation, post-exploitation and persistence technique.
- Corrected PassRole telemetry: `iam:PassRole` has no standalone CloudTrail event; the receiving
  media-pipeline request records the role ARN and downstream service-role activity supplies the
  execution evidence.
- Replaced generic Voice/SIP and media-pipeline logging labels with the actual API families, and
  normalized every expandable section to `Logs generated`. No new AWS calls or resources were
  needed because the existing live authorization/CloudTrail matrix supported the corrections.

## cont.104 (2026-09-30) — Pinpoint push-channel stored-credential boundary

- Rejected `GetBaiduChannel` as a credential-disclosure technique: after storing synthetic API and
  secret keys, both the update and subsequent getter omitted the `Credential` and secret values even
  though the current SDK response model still documents a credential field.
- GCM/FCM could not be proven with a fake key because `UpdateGcmChannel` contacted FCM and rejected
  it as unregistered, even with the channel disabled. The account had no existing projects or GCM
  channels, so no real third-party credential was introduced or accessed.
- Both disposable Pinpoint projects were deleted; exact-ID reads returned `NotFoundException` and
  the matching-name inventory was empty. No book technique or AWS vulnerability report was added.

## cont.105 (2026-09-30) — Route 53 Domains cross-account registration takeover

- SHIPPED #85 (documentation-validated): exact source-account
  `route53domains:TransferDomainToAnotherAwsAccount` plus destination-account
  `AcceptDomainTransferFromAnotherAwsAccount` moves a domain registration into an
  attacker-controlled account after password-backed acceptance.
- The source permission is global `Resource: "*"`; it requires no `ListDomains`, domain detail,
  EPP-code retrieval, transfer-lock write, or PassRole action. The hosted zone remains in the source
  account, but the recipient becomes registration owner and can later alter delegation or transfer
  state using its own account permissions.
- Retrofitted both older Route 53 Domains techniques with explicit minimum prerequisites, impact and
  stealth, and corrected domain-registration CloudTrail event names to their lowercase-first-letter
  form.
- Safe live inventory found zero registered domains. No transfer was attempted, no fixture was
  created, and cleanup was vacuous. Expected functionality only; no AWS report.

## cont.106 (2026-09-30) — Amazon Q in Connect session traces

- SHIPPED #86: `wisdom:ListMessages` can disclose customer/agent/bot text, citations, guardrail
  state and tool results; `wisdom:ListSpans` can expose system instructions, LLM inputs/outputs,
  reasoning, tool calls/results, prompt/model data, contact IDs and guardrail assessments.
- Live least-privilege proof used an inline STS session policy. Both reads reached resource-not-found
  on one exact synthetic Session ARN; another Session ARN and `GetSession` were denied. The reads
  therefore require neither broad session access nor the metadata getter.
- `SearchSessions` independently reached the service with `Resource: "*"`; its current filter is
  exact `NAME EQUALS`, not unfiltered enumeration. The public page documents known-ID fallbacks,
  impact, High/Medium stealth, and `qconnect.amazonaws.com` CloudTrail signals.
- Event History retained the exact IDs/name filter and recorded each failed probe as a read-only
  management event with `responseElements:null`; successful response-body logging remains unclaimed.
- The allowed Region had zero assistants, and no assistant/session was created because sessions have
  no delete API. Two preliminary IAM roles were cleaned and independently verified absent; the final
  STS-policy test created no resources. Expected functionality only; no AWS report.

## cont.107 (2026-09-30) — CodeBuild sandbox interactive connection

- SHIPPED #87: exact-sandbox `codebuild:StartSandboxConnection` returns a Session Manager token and
  stream URL for an interactive shell in a running sandbox, exposing in-container source/secrets and
  the project role without caller-side PassRole, SSM, project mutation, or command-execution rights.
- Live least-privilege proof used an inline STS session policy: the allowed synthetic sandbox ARN
  reached `No sandbox found`, while another ARN and `ListSandboxes` were denied.
- The account contained zero sandboxes, so no end-to-end shell/token was created. Public coverage
  explicitly records the SSM Agent and project-service-role prerequisites and leaves successful
  response logging unclaimed.
- CloudTrail recorded the failed calls as management events with `readOnly:true` despite IAM's Write
  classification; the allowed not-found call retained the exact sandbox ARN.
- No CodeBuild, SSM, or IAM resource was created; cleanup was vacuous. Expected functionality only;
  no AWS report.

## cont.108 (2026-09-30) — Marketplace Deployment buyer-secret poisoning

- SHIPPED #88: a compromised seller principal with product-scoped
  `aws-marketplace:PutDeploymentParameter` can create or replace API keys, OAuth credentials,
  external IDs, license keys or dynamic endpoint parameters in a buyer's Quick Launch managed secret.
- The attack is bounded to a seller-owned product, valid agreement and buyer service-linked role; it
  becomes supply-chain compromise only when the approved template/integration consumes the value.
- Live exact-product authorization reached product-not-found with only `PutDeploymentParameter`.
  Another product and `TagResource` were denied, confirming product scoping and the optional tagging
  dependency.
- CloudTrail recorded the calls as management writes, retained product/agreement/client-token/name,
  and redacted `secretString` as `***`.
- Only impossible synthetic identifiers and a non-secret string were sent. No deployment parameter,
  secret, product, agreement, IAM role or other resource was created. Expected functionality only;
  no AWS report.

## Active 2026-09-26 checkpoint

Research remains active. The September 24 saturation table below records that specific sweep, not completion of AWS research. Recent changes pushed to PR #413 include Account Access Manager role entitlement assignment, Sign-In account and organization console-denial paths, Lambda full-resource-policy code-update escalation, RAM share retention on organization departure, current Organizations departure controls, and stealth/CloudTrail corrections across IAM, Identity Center, Lambda, and Organizations pages. Each tested service has a per-service ledger with prerequisites, negative branches, and cleanup results.

Current next checks: Sign-In network enforcement only in a disposable account; Identity Center applications-only instance effects; resource-share acceptance and retention without moving a production account; broader 2026 IAM/service action coverage. Do not publish unexpected security-impact candidates until separately validated and written in the local private AWS report folder.

Latest verified expected technique: EMR Serverless `GetSessionEndpoint` exact-session permission returns a portable Spark Connect bearer token to a principal other than `session.createdBy`; that client used the existing session's execution role to read a canary it could not access directly. Requires no `iam:PassRole`, `StartSession`, `GetSession`, or `ListSessions`. Public technique and detailed `emr/session-endpoint-2026-09-26.md` evidence added; all disposable test cycles fully cleaned.

Latest negative boundary test: CodeArtifact authorization tokens stayed repository-scoped and both already-issued and newly minted tokens honored a new explicit `ReadFromRepository` deny within 7.6 seconds. Secure result recorded under `codeartifact/`; empty domain/repositories and IAM role fully deleted.

Latest S3 parser boundary test: a 34-case raw SigV4 presigned-POST multipart matrix produced zero objects outside the signed `allowed/` prefix. Duplicate auth/policy/key fields failed safely, traversal filenames stayed prefix-bound, size/SSE conditions held, and old/new forms honored an explicit IAM deny within 15.1 seconds. All 15 objects, bucket, and signer role deleted; zero multipart uploads and no versioning/Object Lock residue.

Well-Architected invitation-recipient binding remains deferred: the safe two-local-user fixture is invalid because `CreateWorkloadShare` rejects a user from the sharer's own account. No invitation was created; workload, both keys/policies, and both users were deleted. Revisit only with an explicitly authorized second account.

Latest documented expected technique: Systems Manager JIT `StartAccessRequest` + `GetAccessToken` vends constrained temporary credentials for an approved Session Manager shell without standing `StartSession` or PassRole. Added with exact prerequisites/impact/stealth/logs. Live test deferred because account preflight found JIT, unified-console setup, approval policies, and managed nodes all absent; no account-wide setting was changed.

## 2026-09-24 sweep checkpoint (historical)

| Axis | State | Notes |
|---|---|---|
| Privesc (existing services) | ✅ complete | impact + "Logs generated" retrofit done across the 28-page privesc tail |
| Post-exploitation (existing) | ✅ complete | impact + logs retrofit done across the 17-page post-ex tail |
| Persistence (existing) | ✅ complete | + Stealth rating on every persistence technique |
| Privesc/post/persistence (net-new services) | ✅ saturated | 34 net-new pages/techniques; phase-2 zero-presence services swept |
| Unauth / recon (all 433) | ✅ complete | 7 new pages + 7 cross-account resource-policy matrix rows; 8-slice manual pass |
| Cross-account resource-policy matrix | ✅ complete | all 75 policy-setters across 433 enumerated; 65 matrix rows |
| autonomous_research folder | 🟡 in progress | this scaffold; per-service checklists being seeded |

**34 net-new pages/techniques + 27 format-fixed** cumulative. HEAD == origin `6f165c07e`. PR #413 body updated through the full unauth sweep.

## The 7 convergent lenses

privesc-PassRole · unauth-authtype · recon-output-shape · persistence · hijack-no-PassRole · per-service-ledger (`master_ledger.csv`) · 8-slice manual review. All converge on "no further clean net-new gap that clears the no-garbage bar." Remaining items are reasoned exclusions (niche/preview/deprecated/cost-blocked) — see each `<service>/tested.md` and `checklist.md`.

## Standing irreversible residue (do NOT re-flag as a mistake)

- `ht-audit-objlock-1790090581` — S3 bucket, one 12-byte object `auto.txt` under COMPLIANCE retain-until **2126-08-29**. Undeletable by any principal incl. account root & AWS Support, by design. ~$0 cost. Verified empirically. Leave it.
- 2 customer KMS CMKs (`1bb73ce3…`, `acdd6d73…`) in PendingDeletion → self-delete 2026-09-29. **Reuse these for KMS tests** instead of creating new CMKs.

Everything else removable in that 2026-09-24 residue sweep was removed. See the current checkpoint above for later test state.

## Known content gaps still worth a page (tracked as per-service checklists)

- ~~ElastiCache — no enum/privesc/post~~ **STALE/WRONG**: `aws-services/aws-elasticache.md` exists with enum + 2 post-ex techniques (ModifyUser password reset, CopySnapshot→S3 exfil) + persistence page. Only a distinct *privesc* framing might be marginally addable (low value).
- MemoryDB — persistence only; no privesc/post.
- ~~Glue — no dedicated enum/deep attack coverage.~~ **CLOSED 2026-09-27**: dedicated enum plus connection/data reads, catalog poisoning, five execution pivots, catalog-policy persistence and recurring-trigger persistence; current PassRole boundaries live-verified in `glue/`.
- `aws-vpn-post-exploitation` — empty stub.
- ~~SSO / Identity Center — persistence angle not yet a page.~~ **STALE/WRONG**: verified cont.66 — `aws-privilege-escalation/aws-sso-and-identitystore-privesc/README.md` comprehensively covers the persistence-relevant primitives (CreatePermissionSet + policy inject + CreateAccountAssignment, identitystore/sso-directory CreateUser, CreateGroupMembership, GetRoleCredentials cache theft, plus Detach/Delete defense-evasion variants). No separate persistence page needed.
- ~~Redshift — privesc+post exist; no persistence/enum-deepen.~~ **CLOSED 2026-09-27**: provisioned and Serverless enumeration, Data API/session/snapshot/datashare coverage, role repointing, admin reset/network/endpoint persistence and deterministic unauthenticated endpoint recon in `redshift/`.

## Net-new since the all-433 sweep

- **AppFabric** (`aws-services/aws-appfabric-enum.md`, 2026-09-24) — zero prior coverage. Enum + `appfabric:CreateIngestionDestination` SaaS-audit-log redirect/exfil + SOC-blinding (authz gate verified, end-to-end doc-scoped due to SaaS-OAuth precondition). Defensive negative: AppFabric does NOT leak stored SaaS credentials via API. See appfabric/.

## Open-idea backlog lives per service

See `<service>/checklist.md`. When an idea is tested it moves to `<service>/tested.md` with the result, and — if it works and clears the no-garbage bar — into the public book.

## Saturation update (cont.61, 2026-09-24)
- Systematic zero-coverage sweep: ALL botocore services cross-referenced vs the whole book -> 133 zero-coverage services; signal-scanned the tail; only ssm-incidents yielded a net-new page. Rest = runtime/data-plane variants, deprecated, no-primitive, or already-deferred.
- Newest 2024 services (bedrock-agentcore) confirmed ALREADY comprehensively covered (token-vault vending, execution-role pivots, sandbox escape, resource-policy) — no net-new.
- This continuation net-new: CloudTrail Lake EDS anti-forensics; Deadline queue-role privesc (VERIFIED live); Incident Manager counter-IR. Cumulative ~40 net-new + 27 format-fixed.
- Remaining threads are compute-gated (Deadline CreateJob->RCE, response-plan/replication-set end-to-end, AgentCore token-vault/payments) -> parked in per-service checklists for a compute-authorized run.

## Saturation update (cont.62-66, 2026-09-24)
- **Net-new this stretch (all pipelined to PR #413):**
  - #42 MWAA classic token->DAG exec-as-execution-role (`airflow:CreateWebLoginToken`/`CreateCliToken`).
  - #43 MWAA exec-role repoint (`airflow:UpdateEnvironment --execution-role-arn` + PassRole) — authz
    VERIFIED. GOTCHA: MWAA IAM prefix is `airflow:`, not `mwaa:`.
  - #44 IoT Core credential-provider role alias (`iot:CreateRoleAlias`/`UpdateRoleAlias` + PassRole ->
    vend any credentials.iot-trusting role via X.509 cert at the cred-provider endpoint) — VERIFIED
    END-TO-END, zero cost. Vend leaves NO CloudTrail event (stealth persistence).
  - #45 Transfer Family role-choice (`transfer:CreateUser`/`UpdateUser`/`CreateAccess` + PassRole binds
    a chosen role to an SFTP identity) — authz VERIFIED. Distinct from pre-existing ImportSshPublicKey.
  - Deadline fleet-role privesc (VERIFIED live, no-compute CMF worker), earlier in stretch.
- **Saturation CONFIRMED across the whole credential/role-vending seam:** Cognito identity pools (SetIdentityPoolRoles/unauth vend/RBAC), SSM CreateActivation, IAM Roles Anywhere (CreateTrustAnchor+Profile / UpdateTrustAnchor / STS privesc), App Runner (CreateService RCE + UpdateService + mutable-tag auto-deploy), Glue GetConnection creds, RDS IAM auth — ALL already documented. The generic PassRole-into-job family is exhaustively catalogued in aws-ml-dataaccess-passrole-privesc (MSK Connect, Braket, m2, Panorama, DAX, pcs, osis, timestream, chime, ... all listed). Net-new only comes from DISTINCT mechanisms the catalog doesn't model.
- **Cumulative: ~45 net-new + 27 format-fixed. All test infra torn down + verified each cycle.**
- **Primed threads for a compute-authorized run:** Transfer custom-IdP Lambda (attacker-controlled auth Lambda mints arbitrary Role/Policy per login); IoT provisioning-template role selection + UpdateCACertificate autoregistration persistence; MWAA end-to-end env exploitation; Deadline CreateJob->RCE-on-worker.

## Saturation update (cont.68-70, 2026-09-25)
- **#47 Lambda exec-role repoint** (`lambda:UpdateFunctionConfiguration --role` + PassRole + Invoke) — authz VERIFIED live (two-sided). Shipped: aws-lambda-privesc/README.md. PR #413. ~47 net-new.
- **Repoint/attach-role lens CONFIRMED SATURATED:** Redshift already covers BOTH `ModifyClusterIamRoles` and serverless `UpdateNamespace` with two-sided PassRole proof; Batch covers RegisterJobDefinition PassRole + SubmitJob (live); CodeBuild/CloudFormation/App Runner/Step Functions all covered. Lambda was the last clean gap in this family.
- **DEAD LENS — "Describe/List returns a stored password":** systematically scanned botocore for read-op output shapes with secret-like fields (password/secret/credential/token/privatekey). Empirically tested the two strongest candidates:
  - AppStream `DescribeDirectoryConfigs.ServiceAccountCredentials` → **AccountPassword REDACTED**, only
    `AccountName` (DOMAIN\user) returned. (appstream/tested.md)
  - DMS `DescribeEndpoints` → **Password removed from output shape**; no value returned. (dms/tested.md)
  - **Calibration:** botocore `sensitive:true` = scrub-from-logs, NOT returned-in-response. AWS redacts
    stored passwords from Describe/List. The ONLY reliable secret vends are purpose-built
    `Get*Credentials`/`GetSecretValue`/`GetAuthorizationToken`/`GetRoleCredentials`/`GetCredentialsForIdentity`/
    `DownloadDefaultKeyPair`/`GetInstanceAccessDetails`/`GetTemporary*Credentials`/`GetDataAccess` — ALL
    already documented (Lightsail, Lake Formation, S3 Access Grants, SSO, Cognito, ECR, CodeArtifact,
    STS, EMR GetClusterSessionCredentials, Redshift GetClusterCredentials, Glue GetConnection).
  - Remaining `sensitive` fields (EMR KerberosAttributes, RDS/docdb/neptune MasterUserPassword, storagegateway
    CHAP, ds SharedSecret, cloudhsmv2 PreCoPassword, wickr OIDC) are the same redacted-in-Describe class →
    not chased. If ever revisited, must be empirically re-tested, not assumed.
- **Cumulative: ~47 net-new + 27 format-fixed.** All test infra torn down + verified each cycle.

## Saturation update (cont.73-74, 2026-09-25)
- **Verified net-new shipped this session:** #47 Lambda UpdateFunctionConfiguration --role repoint; #48 Amazon S3 Files (new page: CreateFileSystem+PassRole data-access + PutFileSystemPolicy cross-account matrix row [66] + mount-target exposure); #49 EKS UpdatePodIdentityAssociation repoint (role swap + target-role cross-account chaining + disable-session-tags ABAC bypass). All authz-verified two-sided.
- **Lenses confirmed saturated/dead this session:**
  - Update*+PassRole "repoint an existing resource's role": saturated after Lambda + EKS (Redshift both
    cluster+serverless, Batch, ECS exhaustive, CodeBuild, App Runner, Step Functions, MWAA, Transfer,
    Amplify all done). Remaining role-input Update ops = niche ML/legacy or no-vend-value (rds:ModifyDBProxy
    role doesn't change configured secret; batch serviceRole limited; s3control:UpdateAccessGrantsLocation
    = marginal Update of documented Create).
  - Code/script injection into an existing execution path: Glue EXHAUSTIVE (StartJobRun --scriptLocation,
    UpdateJob, s3:PutObject on script, workflow stored-authority, blueprints), CodeBuild/ECS/Lambda covered.
  - Describe/List secret-disclosure: DEAD (AppStream/DMS redact; sensitive:true = log-scrub only).
- **New-service frontier:** s3files shipped; iot-managed-integrations parked (irreversible RegisterCustomEndpoint onboarding gate); rest of 2024+ services = no security primitives.
- **Cumulative: ~49 net-new + 28 format/matrix.** All test infra torn down + verified each cycle.

## Saturation update (cont.75) — identity-provider / trusted-token-issuer lens
- SHIPPED (doc-grounded) #50: `sso-admin:CreateTrustedTokenIssuer` rogue TTI → impersonate any Identity Center user via JWT-bearer grant / CreateTokenWithIAM into trusted-identity-propagation apps (Q Business, Redshift, QuickSight, S3 Access Grants). Commit c8980fe16 on research/aws-technique-audit; PR #413 bullet added; autonomous_research/aws/identity-center/{tested,checklist}.md.
- Book-wide grep confirmed TTI/TTP was 0-hit (genuinely undocumented). Lab is Org MEMBER acct (no IdC instance) → doc-grounded per precondition exception; parked end-to-end verify for an IdC-enabled account.
- Identity-provider lens status: IAM SAML/OIDC + Cognito IdP = already covered; TTI = the net-new gap, now shipped. iot:CreateAuthorizer / apigateway:CreateAuthorizer = low IAM-privesc value (app-scoped auth bypass), parked in checklist for possible enum-page mention.

## Saturation update (cont.76) — Batch RegisterJobDefinition+PassRole
- SHIPPED #51 (VERIFIED two-sided): batch:RegisterJobDefinition + iam:PassRole (+ SubmitJob) run-container-as-passed-role, new first section on aws-batch-privesc/README.md. Complements existing SubmitJob-only technique. Commit 6693993d7; PR #413 bullet added.
- Repoint/compute-exec lens sweep: Glue UpdateJob/UpdateDevEndpoint, CodeBuild UpdateProject, Step Functions UpdateStateMachine, CodePipeline UpdatePipeline all covered. Batch's Register+PassRole was the one primary-path gap (only parenthetical before) - now closed.
- Teardown verified: no ht-* roles, no ACTIVE ht-batch-probe defs (INACTIVE remain, no hard-delete available).

## Saturation update (cont.77) — NEW SERVICE Bedrock AgentCore
- SHIPPED #52 (NEW PAGE, 2 techniques VERIFIED two-sided): aws-bedrock-agentcore-privesc/README.md. CreateCodeInterpreter+PassRole (POS created READY interpreter); CreateAgentRuntime(+CreateAgentRuntimeEndpoint)+PassRole (POS advanced past PassRole to endpoint gate, NEG PassRole AccessDenied). + Update-repoint (doc), + data-plane cred vend GetWorkloadAccessToken->GetResourceApiKey/Oauth2Token plaintext (doc, sensitive:true). SUMMARY wired. Commit 1b5051e17; PR #413 bullet.
- Found via comprehensive credential-vend sweep across all 423 botocore services (autonomous_research method). AgentCore = biggest net-new frontier surfaced.
- Calibration reconfirmed: control-plane Get*CredentialProvider returns only Secrets Manager ARN; data-plane GetResourceApiKey returns plaintext (sensitive:true).
- Teardown verified clean.

## Saturation update (cont.78) — SES sending-authorization backdoor
- SHIPPED #53 (doc+partial-verify): ses:PutIdentityPolicy / sesv2:PutEmailIdentityPolicy cross-account sending-authorization backdoor, new section on aws-ses-post-exploitation. Commit 1a0931630; PR #413 bullet.
- Found via all-services resource-policy-setter sweep (Put*Policy/Add*Permission vs cross-account matrix). SES identity policy was a proper-section gap (matrix had only 1 line).
- Other sweep candidates parked/rejected: s3control PutMultiRegionAccessPointPolicy (MRAP cross-account - candidate), signer AddProfilePermission (code-signing cross-account - niche), waf*/PutPermissionPolicy (rulegroup share - low), mediastore PutContainerPolicy (service EOL). Scaling/read policies discarded.

## Saturation update (cont.79) — Budgets CreateBudgetAction privesc
- SHIPPED #54 (NEW PAGE, PassRole gate VERIFIED two-sided): aws-budgets-privesc/README.md. CreateBudgetAction APPLY_IAM_POLICY/APPLY_SCP_POLICY/RUN_SSM_DOCUMENTS + iam:PassRole -> self-attach admin / org SCP / SSM code-exec via ExecutionRoleArn. Execution timing-gated (Standby->Pending on budget eval). Commit 346ff079c; PR #413 bullet.
- Found via all-services Create*/Update* role-passing sweep. Filtered out variant-op noise (sagemaker 21 ops, comprehend/transcribe covered by aws-ml-dataaccess-passrole-privesc). Budgets = genuine net-new (only defensive coverage existed).
- Parked from same sweep for later: kendra (post-exploit only, CreateIndex+PassRole), amplify computeRoleArn, proton (EOL) cross-account connection, ecs ExpressGatewayService (new), guardduty CreateMalwareProtectionPlan.

## cont.80 (2026-09-25)
- Saturation re-confirmed: EventBridge family, SSM CreateActivation (ssm+ecs pages), DataSync/Transfer/FIS/IoT/GameLift privesc, Kendra CreateDataSource+PassRole — all covered.
- SHIPPED #55: AWS AppFlow CreateFlow attacker-defined transfer (aws-appflow-enum.md). Verified live S3->S3 exfil end-to-end; UpdateFlow endpoint-immutability verified; SaaS-connector-profile source doc-grounded. No PassRole (service-linked + connector authority). Residue zero.
- Lens-sweep log cont.76-79 written (parked: s3control MRAP policy, signer AddProfilePermission, finspace-data/emr-containers cred-vends).

## 2026-09-26 Lambda full-policy follow-up
- VERIFIED end-to-end with a least-privilege disposable IAM user: the documented three policy-management permissions work when scoped to one exact function ARN; a PutResourcePolicy attempt against a different ARN was denied.
- The same user was denied Invoke before the full policy and received a successful `200` invocation after the resource policy granted `lambda:InvokeFunction`, despite never having an identity-based invoke allow.
- Teardown verified: function, execution role, IAM user, inline policy, access key, and temporary SDK environment are absent. Zero persistent residue.

## 2026-09-26 S3 Access Grants canonicalization test
- NEGATIVE / secure behavior: a 24-case `GetDataAccess` matrix did not escape an `allowed/*` grant into a sibling `denied/*` object. Accepted dot/encoding strings were scoped literally under `Minimal`; `Default` stayed at the matching `allowed/*` grant. Other variants were denied or rejected as invalid.
- This is research-ledger-only, not public-book content. Full result:
  `s3/access-grants-canonicalization-2026-09-26.md`.
- Two test cycles fully torn down; Access Grants instance, bucket, objects, IAM user/key/policy, and location role/policy all verified absent.

## Saturation update (cont.81) — AgentCore Harness direct shell
- SHIPPED #56 (VERIFIED end to end, two-sided): `CreateHarness` + exact-role `iam:PassRole` + `InvokeAgentRuntimeCommand` produced UID 0 and the target execution-role STS ARN. The no-PassRole principal was explicitly denied. Added enumeration, impact, working boto3 call, logs table, and stealth rating to the AgentCore privesc page; also filled the missing stealth ratings on its four existing techniques.
- Composite-create dependency discovery recorded extra live gates (`CreateAgentRuntimeEndpoint`, `CreateWorkloadIdentity`, `GetAgentRuntime`) and the first-use Runtime Identity service-linked role. Full harness ARN is the working command target; generated runtime ARN and short harness ID are not.
- CloudTrail Event History verified `CreateHarness` request/response logging and exact PassRole denial. Runtime command telemetry attempted `logs:PutLogEvents` under the execution role; without that permission the command still succeeded while CloudWatch export failed.
- Teardown verified: harness, generated managed resources, both IAM users/keys/policies, execution role, and Runtime Identity service-linked role all absent; deletion task `SUCCEEDED`.

## Saturation update (cont.82) — CloudWatch Logs scheduled queries
- SHIPPED #57 (VERIFIED end to end, both role gates isolated): `logs:CreateScheduledQuery` plus `iam:PassRole` on a query execution role and a separate S3 delivery role repeatedly queries log groups the creator cannot read and exports selected rows to S3. No-PassRole denied on the delivery role first; delivery-only PassRole then denied on the execution role; both exact roles with `iam:PassedToService=logs.amazonaws.com` succeeded.
- One synthetic marker was delivered as JSON at the next minute boundary. Added the detailed technique to `aws-cloudwatch-enum.md` and a verified row to the analytics/data-access PassRole matrix.
- CloudTrail verified `CreateScheduledQuery`, automatic `StartQuery`, and automatic `GetQueryResults` as default management events. Creation logs the full query, groups, schedule, bucket URI/owner, and both roles; executions are attributed to `assumed-role/<execution-role>/Logs` with `invokedBy=logs.amazonaws.com`.
- Teardown verified zero scheduled queries, bucket/object, log group, IAM users/keys/policies, or roles.

## cont.83 (2026-09-26) — Step Functions callback-token boundary audit
- NEGATIVE / secure boundary: two isolated Activity cycles verified that callback tokens stayed bound to their original execution and Region; mutation, terminal replay, and expired-token use did not alter a live or closed execution. Exact matrix: `step-functions/callback-token-binding-2026-09-26.md`.
- Two non-security quirks retained for regression: immediate post-success heartbeat replay briefly returned HTTP 200 before converging to `TaskTimedOut`; a one-character token mutation consistently returned `InternalFailure` and generated SDK retries instead of the documented `InvalidToken`. Neither crossed a boundary or changed state, so no AWS vulnerability report and no standalone public attack technique.
- Minimum IAM clarification queued in the public callback technique: `SendTask*` has no resource type and therefore needs `Resource: "*"`; only `GetActivityTask` can be scoped to the Activity ARN.
- Both test cycles torn down. Independent checks found zero matching Activities and IAM roles; deleted state machines entered the service's asynchronous `DELETING` state.

## cont.84 (2026-09-26) — Step Functions dynamic HTTP Task credential capture
- SHIPPED #58 (VERIFIED end to end): `states:StartExecution` alone redirected a fixed EventBridge Connection's API-key header to an account-owned HTTPS collector because the existing workflow sourced `ApiEndpoint` from execution input. The restricted caller's `DescribeStateMachine` was denied and it had no EventBridge, Secrets Manager, update, or PassRole access.
- The execution role needed `states:InvokeHTTPEndpoint` on the exact state-machine ARN, `events:RetrieveConnectionCredentials` on the connection, and Get/Describe on its managed secret. A twenty-second IAM propagation wait was needed; early five-second attempts failed closed.
- CloudTrail showed `StartExecution` with redacted input and a service-driven `GetSecretValue` under the execution role naming the connection secret. The attacker endpoint remained absent without optional `InvokeHTTPEndpoint` state-machine data events or endpoint-side logs.
- Public StartExecution coverage now includes this high-value sink, minimum roles, impact, explicit stealth, logs, and the `states:HTTPEndpoint`/`states:HTTPMethod` mitigations.
- Five disposable cycles fully torn down; final inventory showed no matching state machine, Connection or generated secret, Lambda/Function URL, log group, or IAM role.

## cont.85 (2026-09-26) — TestState HTTP Connection oracle
- SHIPPED #59 (VERIFIED two-sided): `states:TestState` plus exact-role `iam:PassRole` executed an arbitrary HTTP Task and delivered an EventBridge Connection API key to the account-owned collector even with `inspectionLevel=INFO` and `revealSecrets=false`.
- `TestState` alone was denied specifically on PassRole. The positive caller had no `states:RevealSecrets`, EventBridge, Secrets Manager, Lambda, logs, or state-machine CRUD permission. The passed role's endpoint action was conditioned to the exact collector URL/method.
- Added the Connection-specific path, minimum caller/passed-role permissions, impact, stealth, and expanded logging table to the existing Step Functions TestState+PassRole privesc technique.
- Combined fixture torn down and independently verified absent: state machine/execution, Connection/generated secret, Lambda/Function URL, log group, all four roles, and policies.

## cont.86 (2026-09-26) — S3 Tables replication
- SHIPPED #60 (VERIFIED end to end, two-sided): `s3tables:PutTableBucketReplication` plus exact-role `iam:PassRole` configured continuous bucket-level table replication. Put without PassRole was denied on the exact role; initial Put with PassRole succeeded without Get and returned the version token.
- Bucket-level behavior was confirmed across destination replacement: an existing table was created in the new destination while its old replica remained, and a later source table appeared only in the active destination. Deleting the configuration likewise retained both destinations' replicas.
- Existing-rule replacement and deletion failed closed without the current version token. A caller that retained the token from its own previous write needed no Get permission. Empty/no-snapshot tables remained `pending`, so committed data-copy fidelity is explicitly doc-grounded rather than overclaimed as live-tested.
- CloudTrail recorded replication APIs as default management events, but successful Put omitted the entire configuration, replication-role ARN, and destination ARN. Service-driven `CreateNamespace`/`CreateTable` events exposed destination identifiers under the replication role.
- Four disposable cycles were cleaned; final inventory found no matching table bucket or IAM role. Cross-account policy setup is documented but was not live-tested without a second explicitly authorized account.

## cont.87 (2026-09-26) — Transfer Family custom IdP takeover and password exposure
- SHIPPED #61 (VERIFIED two independent end-to-end paths): exact-server `transfer:UpdateServer` alone repointed a Lambda custom IdP, and exact-function `lambda:UpdateFunctionCode` alone poisoned the already-wired IdP. Each accepted an attacker login and a real SFTP session read both protected marker prefixes through the high S3 role returned at authentication. Neither restricted caller had PassRole, Lambda Invoke, direct S3, or logs-read permission; the updater could not even DescribeServer.
- SHIPPED #62 (VERIFIED exact synthetic canary): the Lambda IdP received the SFTP password in plaintext; after the handler intentionally logged its event, `logs:FilterLogEvents` recovered the exact value. Added a dedicated Transfer Family post-exploitation page and SUMMARY entry.
- Filled all four existing Transfer privesc techniques' missing explicit stealth ratings and added the omitted `UpdateAccess` role-choice variant.
- The `PUBLIC_KEY_AND_PASSWORD` matrix enforced both factors and IAM intersection. AWS uses the password response's role/policy/home when factor responses differ; malformed nonempty policies failed closed, password-response PublicKeys were rejected, and empty/omitted Policy intentionally used the base role. Because the trusted IdP already controls authorization, no independent security boundary was crossed; the result stays in the research ledger and no AWS vulnerability report was created.
- Five short endpoint cycles were deleted immediately, never merely stopped. Final independent inventory was empty for matching Transfer servers, Lambdas, IAM roles, S3 buckets, and log groups.

## cont.88 (2026-09-26) — API Gateway custom IdP takeover and test oracle
- SHIPPED #63 (VERIFIED end to end): exact-resource `apigateway:PATCH` on the Transfer IdP's GET/200 integration response plus `apigateway:POST` on that REST API's deployment collection replaced the response template with an attacker-selected role/home. After deployment, a real password SFTP login read the protected S3 marker through that role. The caller had an explicit `iam:PassRole` deny and could not read the integration response.
- SHIPPED #64 (VERIFIED exact-user scope): `transfer:TestIdentityProvider` on one exact user ARN, with `DescribeServer` denied, disclosed the IdP-selected role, home, and API URL. Its caller-controlled `SourceIp` satisfied an IdP allow rule even though a real SFTP login from the actual IP failed; the action creates no session and is documented as post-exploitation recon/password-oracle behavior.
- CloudTrail later confirmed `UpdateIntegrationResponse` records the complete malicious template; `CreateDeployment` records API/stage/deployment; and `TestIdentityProvider` redacts the password but records the chosen source IP plus full IdP response. The latter appeared as `readOnly:false`.
- Two API Gateway test cycles were fully deleted in `finally`, including both Transfer servers, REST APIs, roles/policies, bucket/objects, and access credentials. Combined Transfer custom-IdP inventory remained empty; no server was left stopped or billable.

## cont.89 (2026-09-26) — S3 Express session boundary audit
- SHIPPED #65 (VERIFIED expected data-access behavior): expanded the existing S3 Express `s3express:CreateSession` broker coverage with exact-bucket/minimum IAM, `ReadOnly`/`ReadWrite` impact, High stealth, and an expandable CloudTrail table. Session issuance and object calls are optional S3 Express data events, not default Event History management events.
- NEGATIVE / secure boundary: an exact-bucket-A, `SessionMode=ReadOnly` caller read/listed A but could not write/delete, mint ReadWrite, mint for bucket B, or use its A tuple against B. Omitted mode fell back to ReadOnly as documented.
- Session credential fields were indivisible: mutation, cross-bucket splices, same-bucket ReadOnly / privileged-ReadWrite token splices, and even a splice between two same-scope ReadOnly sessions all failed closed. An intact tuple replayed before expiry; a freshly signed request after its returned five-minute expiration was denied.
- Raw REST required `x-amz-content-sha256` on the empty CreateSession GET. A session-authenticated HEAD against its own Zonal bucket returned 200 despite documentation preferring IAM credentials; the same tuple against bucket B returned 403, so this remains a compatibility note without security impact and no AWS vulnerability report.
- Three complete two-bucket cycles and two preliminary header-diagnostic cycles ran through `finally`. Every object, directory bucket, inline policy, and test role was deleted; independent inventory for the `ht-s3e-` prefix was empty.

## cont.90 (2026-09-26) — Aurora DSQL authentication-token boundaries
- SHIPPED #66 (format + verified semantics): filled explicit impact, stealth, and expandable logs tables for all three existing Aurora DSQL techniques (`DbConnectAdmin`, `DbConnect`, and `PutClusterPolicy`). Added the verified fact that token generation is local/invisible while every new connection re-evaluates current IAM and IAM-to-database-role mapping state.
- NEGATIVE / secure boundary across two live clusters: correct admin/custom tokens connected, while action/user swaps, an unmapped principal, cluster-A token on B, exact-A IAM scope on B, wrong-Region signing, action/host/signature/security-token mutations, and a duplicate Action parameter all failed.
- Normal unchanged replay before expiry worked as documented. A 60-second token was rejected after 75 seconds. Revoking the database-role mapping immediately invalidated a still-live token, restoring the mapping restored that same token, and deleting `DbConnect` IAM authorization invalidated it again.
- Token generation produced no AWS call. Connection attempts require optional `AWS::DSQL::Cluster` data events; SQL is not CloudTrail API activity. Default Event History contained both CreateCluster and both DeleteCluster fixture events.
- Both empty clusters reached not-found, all mappings/database roles were removed best-effort, all three IAM roles/policies were deleted, and no Aurora DSQL service-linked role remained. Independent cluster and IAM inventories were empty. No AWS vulnerability report.

## cont.91 (2026-09-26) — Transfer Family logging defense evasion
- SHIPPED #67 (VERIFIED exact-server minimum): `transfer:UpdateServer` alone cleared both legacy `LoggingRole` and structured destinations on an ONLINE server. The restricted caller could not DescribeServer and had explicit denies on every `logs:*` action and `iam:PassRole`.
- Individual clears preserved the other logger; a fresh server with both configured accepted `LoggingRole:""` plus `StructuredLogDestinations:[]` together in one call and immediately described with both empty while remaining ONLINE.
- Published as post-exploitation/defense evasion, not persistence. It suppresses future Transfer CloudWatch protocol telemetry but does not erase history, hide the default `UpdateServer` management event, or disable independently enabled S3 data events.
- Re-enabling a structured destination immediately after clearing it returned a delivery-conflict error for at least 150 seconds. This rollback lag is recorded as an operational caveat, not a new permission or security boundary.
- CloudTrail retained the exact empty logging fields in the default `UpdateServer` management event (`readOnly:false`); no separate caller-attributed `DeleteDelivery` event was found after propagation.
- Three disposable endpoint cycles were deleted, never stopped. Independent inventory was empty for matching servers, log deliveries/groups, IAM roles, and inline policies. Total cost remained far below the authorized ceiling.

## cont.92 (2026-09-26) — Amazon Location API-key boundaries and persistence
- SHIPPED #68 (VERIFIED exact-resource minimum): `geo:CreateKey` plus the exact delegated `geo-maps:GetTile` permission minted a no-expiry public bearer key that remained usable after its creator IAM role was deleted. `CreateKey` alone failed, and an update could not add Places access that the issuer lacked, so this is service-level persistence rather than privilege escalation.
- SHIPPED #69 (format + verified semantics): corrected the Location unauthenticated-access page to explain that `AllowReferers` matches a caller-controlled header. Missing and confused referrers failed, while a custom client supplying the exact allowed value succeeded by design. Added explicit impact, High stealth, optional provider-data-event logging, and honest action/resource/Region negatives.
- Secure parser/boundary results: wrong Region, cross-service Places, unauthorized static-map action, malformed key, uppercase parameter name, and header-only key all failed. Percent-decoded `k%65y` worked as the same logical name; duplicate query keys selected the last value without composing permissions, so no parser/authz desynchronization was found.
- Recently used keys required documented `ForceUpdate`/`ForceDelete`. Tightening applied immediately. Three update-then-delete repetitions accepted one immediate request and rejected by two seconds; one earlier cycle lasted at least seven seconds. Recorded as a short distributed invalidation caveat, not a vulnerability, with broader timing tests left open.
- Event History confirmed that `CreateKey` records complete actions/resources and `NoExpiry` but redacts the returned key as `***`; `UpdateKey` redacts referrer values while exposing actions, resources and `ForceUpdate`; `DeleteKey` records `forceDelete:true`.
- Every disposable key was force-deleted; final `HTLocation*` inventory was empty and the test role did not exist. No maps, VPCs, compute, or logging fixtures were created. No private AWS report.

## cont.93 (2026-09-26) — Transfer Family Secrets Manager identity poisoning
- SHIPPED #70 (VERIFIED end to end): exact-secret `secretsmanager:PutSecretValue` replaced a legacy custom-IdP user's password and selected a high Transfer role. A real SFTP login read the protected marker while the baseline role had been denied it. The restricted caller could not Get the secret, pass a role, mutate Transfer/Lambda/API Gateway, or access S3 directly.
- The successful new version automatically became `AWSCURRENT`; the old password stopped working. The escalation is limited to S3/EFS operations Transfer performs through the pre-existing trusted role and does not return STS credentials.
- The AWS-managed `aws/secretsmanager` key needed no positive KMS grant, but a preliminary explicit `Deny kms:*` blocked `PutSecretValue` because Secrets Manager requests a data key on the caller's behalf. Customer-managed keys retain their KMS authorization gate.
- Public coverage is explicitly limited to legacy/compatible IdPs that store authorization fields in the secret. The newer toolkit keeps Role/Policy/home in DynamoDB; that datastore mutation remains a separate open test.
- Two disposable server cycles were deleted, never stopped. Final independent inventory was empty for matching Transfer servers, REST APIs, Lambda functions/log groups, secrets, S3 buckets, and roles. API Gateway account settings were never touched. Expected functionality; no private AWS report.

## cont.94 (2026-09-26) — Timestream deferral and IVS Chat token boundaries
- Timestream Query's unusually explicit `NextToken` principal/query/five-use/parent-child guarantees were converted into a bounded test plan. Preflight stopped cleanly because the account is not an existing LiveAnalytics customer; both `ListDatabases` and `DescribeEndpoints` returned the documented closed-new-customer AccessDenied. No Timestream or IAM resources were created.
- NEGATIVE / secure boundary: an exact-room `ivschat:CreateChatToken` caller minted a synthetic token while List/Get and a different room ARN were denied. Sequential replay, mutation, wrong-Region use, and a duplicate while the first socket was live all failed with HTTP 400; the untouched first use returned HTTP 101.
- Five independent eight-way races each produced exactly one HTTP 101 and seven HTTP 400 results, confirming atomic enforcement of the documented single-use property under the tested concurrency. Raw tokens were never logged, messages were not sent, and no AWS vulnerability report was created.
- Filled the existing IVS Chat technique's missing explicit impact, stealth, minimum permission, and expandable log table. The disposable room and exact-room minter role/policy were removed; final IVS Chat and IAM inventories were empty.

## cont.95 (2026-09-29) — Wickr stored credentials and invitation footholds
- SHIPPED #71 (documented model + exact-resource authorization): `wickr:GetOpentdfConfig` directly returns an OpenTDF client ID and secret without Secrets Manager, KMS, or IdP permissions. Published the resulting client-credential access with explicit scope/entitlement limits.
- Completed the existing `GetOidcInfo` coverage: the response contains distinct stored secret fields; optional access/ID/refresh-token output still requires a valid caller-supplied OAuth flow and was not presented as automatic token minting.
- SHIPPED #72 (preview API, conditional): `wickr:ListUsers` exposes invite codes and invitation state. An unexpired pending code can provide a Wickr application foothold with the invited user's groups, but not that user's IAM identity.
- Retrofitted the data-retention-bot challenge technique with exact-network minimum permission, explicit impact, Low stealth, and an expandable telemetry table.
- Safe signed probes confirmed Wickr management-event telemetry. Observed requests recorded network identifiers but omitted tested OIDC parameters and response bodies; successful secret response logging remains deliberately unclaimed because the account had no configured network.
- No networks existed in either allowed Region and no resources were created. Bot reset/admin session and three possible validation/request-relay paths remain private, fixture-dependent test ideas; no AWS vulnerability report was created.

## cont.96 (2026-09-29) — API Gateway developer-portal boundaries
- SHIPPED #73 (documented model + exact-resource authorization): `UpdatePortal` can replace Cognito authorization with `None`; `PublishPortal` makes the documentation/catalog internet-accessible. The minimum includes both exact-portal writes and dependent `GetPortalProduct` on included products, but no Cognito administrator action or `iam:PassRole`.
- SHIPPED #74: documented unauthenticated public-portal recon, the conditional Cognito self-sign-up foothold, and the fact that **Try it** retains endpoint authorization and excludes private, mTLS, and private/self-signed-certificate APIs.
- SHIPPED #75 (cross-account): an AWS RAM PortalProduct share lets a recipient add owner-maintained API documentation to its own portal. The live default permission was read-only and did not grant API invocation, source mutation, or re-sharing.
- Safe reads found no portals/products in either allowed Region. Signed not-found requests generated API Gateway management events; no service, RAM, Cognito, or IAM resources were created.
- Endpoint-page IDOR, Try-it request relay, `logoUri` confused-deputy, stored XSS, preview-link, and foreign-Cognito-pool ideas remain private fixture-dependent tests. No AWS vulnerability report.

## cont.97 (2026-09-29) — AWS Artifact reports, agreements, and inquiries
- SHIPPED #76 (verified exact-report minimum): `GetTermForReport` plus `GetReport` generates a short-lived AWS-owned S3 URL for a confidential compliance report without customer S3 permission. Public coverage includes watermark attribution, acceptance-type/ARN caveats, impact, and telemetry.
- SHIPPED #77 (documented current APIs + safe reads): mapped the complete tokenized account-agreement acceptance and customer-agreement termination workflows. These can change durable legal/compliance state, potentially organization-wide only with the documented management-account prerequisites; no write was performed.
- SHIPPED #78 (documented model): Assurance Assistant inquiry reads/export can disclose uploaded questionnaires, generated answers, citations, revisions, metadata/tags, and a presigned export. The account had no inquiries, so exact newer-event response logging remains explicitly unclaimed.
- Inventory found 397 reports (63 explicit-acceptance), ten available account agreements, no accepted customer agreements, and no compliance inquiries. No document URL was redeemed and all disposable IAM roles/policies were deleted; final matching-role inventory was empty.

## cont.98 (2026-09-29) — AWS Interconnect activation keys and Entity Resolution correction
- SHIPPED #79 (exact-resource minimum verified): `interconnect:GetConnection` returns the sensitive partner activation key used to complete a pending multicloud/last-mile connection. Published the conditional network-path impact, partner-account/state gates, and explicit non-IAM limitations.
- A role scoped to one synthetic connection reached `ResourceNotFoundException` while a different ID was denied. A separate list-only role returned empty inventory and could not call the getter. Both roles/policies and temporary scripts were deleted; final `ht-interconnect-*` inventory was empty.
- Interconnect inventories were empty in both allowed Regions. Unsigned calls required SigV4; no connection, Direct Connect gateway, route, or provider workflow was created. CloudTrail confirmed read-only management events and the official example redacts activation keys.
- Corrected Entity Resolution provider enumeration: current `provider-service-name` requires the full AWS-managed provider-service ARN, which can use a different catalog Region and has a blank account field. Added the provider credential **secret-ARN** disclosure boundary without implying secret-value access. Existing high-value Entity Resolution attacks remain complete; no AWS defect was found.

## cont.99 (2026-09-29) — Backup Search export authorization correction
- Corrected the existing export technique: omitting optional `RoleArn` requires only exact-job `backup-search:StartSearchResultExportJob`; the custom-role form additionally needs exact-role PassRole with `iam:PassedToService=backup-search.amazonaws.com`.
- Kept role trust (`backup.amazonaws.com`) distinct from the PassRole context, documented optional tagging/KMS dependencies, exact export-job reads and the absence of presigned URLs/content access.
- Both allowed Regions finished with zero search/export jobs and indexes; disposable IAM fixtures and scripts were deleted. Expected functionality only; no AWS report.

## cont.100 (2026-09-29) — Security Incident Response account oracle and defense impairment
- SHIPPED #80 (exact-resource model + failed-call telemetry):
  `BatchGetMemberAccountDetails` classifies up to 100 already-known account IDs per request by organization and membership relationship without Organizations or membership-read permission.
- Promoted exact-membership triage/OU-coverage impairment and immediate `CancelMembership` destruction, plus the Organizations management-account path for delegated Security IR membership termination. All are deliberately labeled with their documented/live confidence and noisy signals.
- Corrected CloudTrail claims: sensitive case/contact/attachment fields are redacted and read responses do not log returned presigned URLs. Narrowed attachment poisoning to the self-managed customer workflow and documented the central-account/no-resource-policy boundary.
- No paid membership or infrastructure was created. Both Regions remained empty; no AWS defect or private report resulted.

## cont.101 (2026-09-29) — AWS DevOps Agent integration and persistence boundaries
- SHIPPED #81: sanitized registered-service/association recon exposes endpoints, resource selection, roles, auth methods and provider identifiers without returning stored credentials.
- SHIPPED #82: association overwrite/update can poison monitoring, resource and MCP-tool selection; webhook-capable association creation can additionally return a one-time external bearer credential that persists at agent-space level after the AWS session ends.
- SHIPPED #83: private-connection certificate replacement gives an immediate outage path and, conditional on destination/network control, credential interception or malicious tool responses.
- Corrected the stale IdP-swap page: `UpdateOperatorAppIdpConfig` only rotates the secret. Full IdP replacement requires noisy Disable+Enable plus PassRole to `aidevops.amazonaws.com`.
- Both Regions had zero spaces/services/private connections; no resources or third-party requests were created. Provider credential-relay and private-connection SSRF ideas remain private, fixture-dependent hypotheses; no AWS defect or report.
