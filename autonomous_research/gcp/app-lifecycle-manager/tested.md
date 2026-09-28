# App Lifecycle Manager security research ledger

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
