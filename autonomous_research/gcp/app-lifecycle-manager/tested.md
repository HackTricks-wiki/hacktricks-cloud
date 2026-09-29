# App Lifecycle Manager security research ledger

## 2026-09-29 — standalone feature-flag control, runtime proof and remote MCP

- Created the documented standalone topology in global plus `us-central1`: matching SaaS and
  UnitKind resources, one non-provisioning Unit, a Boolean flag, immutable revision, FlagRelease,
  RolloutKind and global/regional child Rollout. The initial rollout succeeded and the Unit exposed
  its regional `featureFlagsConfig` with the expected revision despite remaining
  `UNIT_STATE_NOT_PROVISIONED`, confirming that flag-only use does not require infrastructure
  deployment.
- A separate runtime identity holding only `roles/saasconfig.viewer` plus Service Usage Consumer
  successfully streamed the regional flagd document. With authoritative default `Disabled=false`,
  the client returned `False`, reason `STATIC`, variant `Disabled` and no evaluation error.
- Reduced the writer to a custom project role containing exactly
  `saasservicemgmt.flags.{get,update}`, `saasservicemgmt.flagRevisions.create`,
  `saasservicemgmt.flagReleases.create`, `saasservicemgmt.rollouts.create`, and
  `saasservicemgmt.operations.get`, plus Service Usage Consumer. It had no Compute, deployment,
  IAM mutation, actAs, token-mint or SaaS Config runtime-read role.
- The reduced writer changed the flag default to `Enabled`, created revision 2, created release 2,
  and initiated rollout 2. Both global and regional rollouts reached `ROLLOUT_STATE_SUCCEEDED`, the
  Unit changed to the regional revision 2, and the independent runtime identity then returned
  `True`, reason `STATIC`, variant `Enabled` with an explicitly opposite `False` fallback. This
  directly verifies application-configuration impact without a code or infrastructure deployment.
- The live aggregate MCP endpoint exposed 35 tools: 24 read-only list/get tools and 11 create tools.
  It includes create tools for SaaS, Tenant, UnitKind, Unit, UnitOperation, infrastructure Release,
  RolloutKind, Flag, FlagRevision, FlagRelease and FlagAttribute. It has list/get but no create tool
  for Rollout, and has no update/delete tools, so it cannot complete the existing-flag update chain
  by itself.
- Anonymous `tools/list` returned HTTP 200 and all 35 schemas; anonymous `tools/call` returned 401.
  An authenticated caller with backend `flags.get` but without `mcp.tools.call` received an explicit
  wrapper denial. After adding only `roles/mcp.toolUser`, `get_flag` succeeded. A `create_flag`
  `validateOnly` request then failed specifically on absent `saasservicemgmt.flags.create`, proving
  the wrapper role does not bypass backend IAM.
- The four initiating writes appeared as always-on Admin Activity under the reduced writer:
  `SaasFlags.UpdateFlag`, `CreateFlagRevision`, `CreateFlagRelease`, and
  `SaasRollouts.CreateRollout`. Regional replication generated service-agent `UpdateUnitKind`,
  replicated `CreateFlag`, `CreateUnitOperation`, and `UpdateUnit` activity. Flagd `SyncFlags` and
  `FetchAllFlags` are documented `DATA_READ` SaaS Config events and are disabled by default; MCP
  wrapper telemetry is independently disabled-by-default Data Access.
- Cleanup first recovered and deleted the stale run-owned `alm-saas-0928233538` object left by the
  earlier Preview teardown. For the current fixture it deleted both root/child rollouts, RolloutKind,
  global and replicated regional releases/revisions/flags, Unit, both UnitKinds and both SaaS
  resources. Clearing `defaultFlagRevisions` on both UnitKinds was required before the final
  revision deletes. Both service-generated Artifact Registry repositories were deleted explicitly.
- Removed both disposable identities and keys, every project binding, the custom role, the managed
  service-agent binding, gcloud configurations and local artifacts. Both APIs were restored to their
  disabled baseline. Exact IAM, service-account, repository, configuration and `/tmp` inventories
  were empty, and a final API probe returned `SERVICE_DISABLED`.
- Retained one high-value expected post-exploitation technique: application-defined behavior
  manipulation through the flag revision/release/rollout chain. It is not automatically cloud IAM
  escalation and is specially noisy because every control-plane write is Admin Activity. No
  authorization vulnerability was found in the flag or MCP control planes.

## 2026-09-28/29 — current Release, UnitOperation, Rollout and identity boundary

- Reviewed current official v1 discovery revision `20260914`, local Google Cloud SDK 586.0.0 beta
  help, predefined roles, service-agent role, audit matrix, platform-log guide, blueprint workflow,
  variable precedence, and deletion dependencies.
- Retained one high-value expected privilege-escalation primitive. A Release accepts an OCI Terraform
  blueprint; a direct upgrade UnitOperation applies it to one provisioned Unit and a Rollout applies
  it across a RolloutKind population. Existing Unit inputs participate in precedence, including the
  prepared `actuation_sa`, so replacing blueprint content can make the service mutate infrastructure
  with that account's effective permissions.
- Exact caller writes are `saasservicemgmt.releases.create` plus
  `saasservicemgmt.unitOperations.create`, or plus `saasservicemgmt.rollouts.create` for fleet mode.
  All are in `roles/saasservicemgmt.admin` and basic Editor/Owner; none is in the Viewer role. The
  Admin role contains no IAM service-account attachment or token-mint permission. This is documented
  product authority, not an authorization vulnerability.
- Bounded the technique to an existing provisioned Unit, valid UnitKind, readable compatible OCI
  blueprint, prepared actuation account, usable Infrastructure Manager and service-agent chain,
  target APIs/policies/quotas, and RolloutKind scope. An arbitrary account email does not become a
  working actuation identity merely because it is supplied as a variable.
- A bounded bootstrap was attempted with digest-pinned synthetic OCI Terraform, an isolated caller
  holding only App Lifecycle Manager Admin plus Service Usage Consumer, and a separate actuation
  account. The caller's ALM role needed an explicit service-readiness wait after IAM binding.
  Creating a SaaS offering also caused the ALM service agent to create a separate system-named
  Artifact Registry repository, a cleanup dependency not exposed by the normal repository list.
- The low-level Preview topology did not reach a provisioned Unit. With global UnitKind/Release and
  a regional Unit, `CreateUnit` authorized `saasservicemgmt.units.create` but failed while reading
  the referenced project/UnitKind. The same result occurred for both the project Owner and the
  isolated in-project ALM Admin, and temporarily adding Browser to the ALM service agent did not
  change it. Moving UnitKind regional caused `CreateUnitKind` to fail while reading the documented
  global SaaS parent. Current setup documentation routes UnitKind population through App Design
  Center composite templates, so an empty low-level UnitKind is not a valid substitute for an
  already prepared fixture.
- No Unit, UnitOperation, Infrastructure Manager deployment, target marker, Rollout, or retained-SA
  actuation occurred. The privilege-escalation entry therefore remains documentation-grounded for
  an existing valid deployment; the exact two-write custom-role minimum and live downstream
  principal are not claimed. This bootstrap behavior is not a security vulnerability.
- Audit coverage is strong: v1 and v1beta1 CreateRelease, CreateUnitOperation, and CreateRollout are
  always-on Admin Activity (the current beta CLI uses v1beta1); UnitOperation/Rollout platform logs
  expose state; Infra Manager and the target services provide downstream control-plane records.
  Artifact/state Data Access visibility depends on those services' configurations.

## Dismissed or deferred claims

- Release `blueprint.package` and `unitKind` are immutable in the current schema, so do not claim an
  in-place Release blueprint swap. Create a new malicious Release instead.
- A Rollout `unitFilter` can only reduce, not expand, its RolloutKind scope. Do not describe it as an
  arbitrary cross-UnitKind targeting bypass.
- Viewer access exposes topology, blueprint URIs, and resolved variables but is not by itself a
  strong post-exploitation technique unless a real deployment stores sensitive values there.
- The failed-operation or caller-`actAs` behavior has not been observed live. Keep any discrepancy
  between documented actuation and live authorization private-first until reproduced end to end.
- Teardown removed every run-owned SaaS/UnitKind/Release, both explicit and system-created Artifact
  Registry repositories, identities, keys, IAM bindings, service agents, local configs/builders,
  and the two APIs absent at baseline. Authoritative inventory is empty; Cloud Asset retains only
  transient tombstones for deleted service-account keys.
