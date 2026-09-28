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
