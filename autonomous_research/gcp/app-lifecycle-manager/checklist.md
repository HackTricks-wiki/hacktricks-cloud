# App Lifecycle Manager security research checklist

## Completed documentation and bootstrap checks — 2026-09-29

- [x] Map SaaS, UnitKind, Unit, Release, UnitOperation, RolloutKind, and Rollout relationships.
- [x] Verify Release blueprint immutability, Unit input-variable retention, Release defaults, and
      UnitOperation override precedence.
- [x] Verify exact Release, UnitOperation, and Rollout create permissions and predefined-role
      membership; separate caller permissions from service-agent and actuation-account prerequisites.
- [x] Verify exact Admin Activity methods and the separate UnitOperation/Rollout platform logs.
- [x] Add enumeration and privilege-escalation pages with bounded impact, categorical stealth, and
      expandable telemetry.
- [x] Attempt a clean Preview bootstrap with synthetic digest-pinned OCI blueprints and isolated
      identities. Record the global/regional reference failures, IAM propagation gate, hidden
      service-created Artifact Registry repository, and full zero-diff teardown.

## Safe live-validation leads

- [x] Validate the new feature-flag control plane with synthetic standalone resources: create a
      flag, immutable revision, release and rollout, prove that the selected Unit receives the new
      value through `saasconfig.googleapis.com`, then delete every resource. Reduce the caller to
      exact `flags.*`, `flagRevisions.*`, `flagReleases.*` and `rollouts.create` permissions.
- [x] Confirm whether changing a live flag revision/release can alter authorization or debug behavior
      in a deliberately instrumented test application without any infrastructure deployment
      permission. Publish as application post-exploitation only if the flag-to-unit propagation and
      impact are directly observed.
- [x] Map the live 35-tool `saasservicemgmt.googleapis.com/mcp` surface. In particular, verify the
      independent `mcp.tools.call` gate and whether `create_flag`, `create_flag_revision` and
      `create_flag_release` preserve the same underlying authorization and Admin Activity logging as
      the REST methods.
- [x] Test whether `flagReleases.create` plus `rollouts.create` can republish a historical revision
      without flag get/update or revision-read authority. The exact three-permission caller restored
      the older value while the global Flag kept its newer default; retain as a distinct rollback
      technique and detect Unit/release revision drift.

- [ ] Test targeted evaluation rules, `FlagAttribute` writes and dynamic allocations against two
      disposable Units. Determine whether a caller can influence one tenant/cohort without changing
      the default, and document only if the targeting adds meaningful offensive value beyond the
      verified fleet-wide flag-control primitive.
- [ ] Test cross-project and guessed `featureFlagsConfigs` provider IDs with exact SaaS Config
      Viewer/custom permissions. Expected result is strict project/resource IAM enforcement; keep
      any cross-project or cross-tenant read discrepancy private-first.
- [ ] Recheck the remote MCP tool inventory after Preview revisions, especially for a future
      `update_flag` or `create_rollout` tool that would make the complete application-control chain
      agent-callable.

- [ ] In an already prepared disposable App Lifecycle Manager fixture, provision a benign Unit with
      a zero-risk actuation account, then give an isolated caller only Release create plus
      UnitOperation create. Apply a second blueprint that writes a synthetic marker using the
      retained `actuation_sa`; confirm the caller has neither actAs nor target-resource permission.
      Do not substitute an empty low-level UnitKind: use the current App Design Center composite
      template setup or a known-good existing Unit.
- [ ] Repeat through Rollout create against two labeled Units and verify the reducing `unitFilter`,
      RolloutKind boundary, generated child UnitOperations, principals, and state/platform logs.
- [ ] Test whether a Release default or UnitOperation override can replace `actuation_sa` without
      caller `actAs`. Treat use of an already prepared identity as expected functionality; keep an
      arbitrary cross-project attachment discrepancy private-first.
- [ ] Test cross-project/private Artifact Registry blueprint pulls and record the exact reader
      identity and `downloadArtifacts` failure. Never expose a credential or use an unowned registry.
- [ ] Restore the benign Release, wait for rollback completion, deprovision Units, and delete in
      dependency order: operations/rollouts, Units, Releases, RolloutKinds, UnitKinds, SaaS,
      Infrastructure Manager deployments/revisions, artifacts/repository, buckets, identities,
      bindings, service agents created solely for the test, and APIs absent at baseline.

## Do not publish without stronger evidence

- [ ] Do not claim direct service-account token theft; the verified impact is Terraform-mediated
      infrastructure mutation within the actuation account's permissions.
- [ ] Do not claim a Release can be mutated to point at another blueprint; that field is immutable.
- [ ] Do not claim a Rollout filter expands beyond the associated RolloutKind.
- [ ] Do not label documented Admin authority a vulnerability merely because the role lacks caller
      `iam.serviceAccounts.actAs`.
