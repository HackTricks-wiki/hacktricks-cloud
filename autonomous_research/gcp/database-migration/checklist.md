# Database Migration Service — open questions

- [ ] With an existing authorized source profile and a controlled destination, live-test the exact minimum DMS and destination permissions for migration start and continuous promotion. Do not infer a cross-project data path from the service-agent role alone.
- [ ] Check whether a caller with `migrationJobs.create` can reference a source connection profile they cannot read, and whether DMS evaluates resource-level IAM on the profile. A successful unauthorized reference would be a potential boundary failure; do not publish without an isolated test.

## 2026-09-28 follow-up

- [x] Separate caller permissions from DMS service-agent, source-database, destination, and network authority.
- [x] Verify the Cloud SQL destination-profile creation flags and migration-job create/start/promote syntax against stable local CLI help.
- [x] Map the candidate path to exact DMS v1 audit methods and default visibility.
- [x] Remove IAM-only, recon, connectivity-only, unsupported conversion-injection, and raw service-agent-role claims from the privilege-escalation page.
- [ ] With a disposable source and a strict cost cap, test whether `connectionProfiles.create` can provision its new Cloud SQL replica when the caller has `datamigration.connectionprofiles.create`/`operations.get` but **no** `cloudsql.*` permissions. The generic REST page lists only the DMS permission, but the PostgreSQL API guide requires Cloud SQL Admin. Treat this as an unresolved boundary hypothesis, not a book technique; delete the profile and destination immediately.
- [ ] If DMS-only destination creation succeeds, test the complete custom-role path containing the four DMS mutations plus `datamigration.operations.get`, `connectionprofiles.get`, and `migrationjobs.get`. Record Service Usage, profile-reference, destination, and network checks, then delete the job, profiles, and destination instance.
- [ ] Test whether `migrationJobs.create`/`start` accepts a known source-profile resource name when the caller lacks that profile's `get` permission. The create REST page lists only `datamigration.migrationjobs.create`, but cross-resource authorization must not be inferred without a live test.
- [ ] Capture live audit entries to verify the service-agent principal and exact downstream Cloud SQL methods for DMS-created destination provisioning and promotion.
- [ ] Separately validate the analogous AlloyDB destination-profile path (`connection-profiles create alloydb`) and its public-IP/authorized-network behavior before expanding the public technique beyond Cloud SQL.

## 2026-09-28 independent cross-review

- [x] Reconcile the generic v1 `connectionProfiles.create` permission table with both the PostgreSQL
      API guide and the current quick-start role/permission list.
- [x] Confirm from local SDK 586.0.0 that `connection-profiles create cloudsql` constructs
      `CloudSqlSettings` and calls the DMS `CreateConnectionProfile` method; it does not make a
      caller-side Cloud SQL create request.
- [x] Recheck input-only passwords/TLS private keys, service-agent permissions, audit method names,
      audit classes, and LRO behavior.
- [x] Retain zero public H3s pending a least-privilege runtime result.
- [x] Record the current lab constraint: the DMS API is disabled and no DMS service agent or binding
      exists. Do not enable it merely for this test because the managed identity might remain.
- [ ] For the existing custom-role test, separate the initial asynchronous create authorization from
      `datamigration.operations.get`: submit the raw REST create request first, then poll with a
      separately controlled principal or permission set. Record whether the DMS operation, Cloud SQL
      instance, or neither is created when the caller lacks every `cloudsql.*` permission. Use a
      disposable whole project, strict cost cap, immediate resource cleanup, and project deletion so
      service-agent residue is not left in the shared lab.
- [ ] Do not extrapolate the Preview quick-start permission list to the legacy Cloud SQL connection-
      profile endpoint. Test that endpoint and the AlloyDB endpoint independently because their
      downstream authorization may differ.

## Exact no-residue plan for the Cloud SQL boundary test

- Use only an already-DMS-enabled disposable project that can be deleted after the test. Do not
  enable DMS in the shared lab: the currently absent Google-managed service agent might survive an
  API disable and violate the cleanup requirement.
- As the administrator, create an inert MySQL source profile that points to TEST-NET-1
  (`192.0.2.1`) and carries a unique run label. The source does not need to be reachable when the
  profile is stored.
- Give the restricted test principal only `datamigration.connectionprofiles.create`,
  `datamigration.connectionprofiles.get`, `datamigration.operations.get`, and
  `serviceusage.services.use`; verify that it has no `cloudsql.*` permission. Submit only the Cloud
  SQL destination-profile creation as that principal, using the inert source profile, a ZONAL
  `db-n1-standard-1` MySQL 8.0 destination, a 10-GB PD_HDD disk, random disposable passwords, and
  the same unique run label.
- Treat an immediate `cloudsql.instances.create` denial or a later LRO failure for missing Cloud SQL
  authority as rejection of the complete escalation. Treat it as confirmed only if the operation
  succeeds, the destination profile exposes a non-empty `cloudsql.cloudSqlId`, and the principal's
  lack of every `cloudsql.*` permission is independently demonstrated.
- Never guess the replica name: the create request has no separate instance-ID field. Capture the
  output-only `cloudsql.cloudSqlId` from the destination profile before cleanup. If profile creation
  partially fails, enumerate Cloud SQL instances by the unique run label.
- Cleanup as the administrator after the operation reaches a terminal state: force-delete the
  destination profile, explicitly delete the captured or label-discovered Cloud SQL instance if it
  remains, delete the inert source profile and DMS operation record, remove the custom-role binding,
  service account and custom role, and finally delete the disposable project. Recheck both DMS and
  Cloud SQL inventories before declaring the test clean.
