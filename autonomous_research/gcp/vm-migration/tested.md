# VM Migration security research

## 2026-09-28 — official-contract and local CLI audit

No cloud resource, API state, IAM policy, source, migration, clone, or image import was created or
changed. Evidence came from current official Google Cloud documentation, the v1 discovery document,
local `gcloud` help, and live predefined-role metadata.

### Retained findings

- **Target-metadata execution under an existing runtime service account (privesc).**
  `computeEngineTargetDefaults.metadata` accepts startup-script keys. A field-specific
  `UpdateMigratingVm` followed by `CreateCloneJob` can execute as root in the clone and request
  the already configured runtime service account's metadata token. The host-project VM Migration
  service agent performs deployment and must already have `iam.serviceAccounts.actAs` on that
  runtime identity.
- **Clone a replicated VM (post-exploitation).** `vmmigration.cloneJobs.create` alone is sufficient
  when a replicated VM already has deployable target defaults. The clone is made from the latest
  successful replicated snapshots and is non-disruptive to the source. Reading it still requires
  access to the target VM/disks or an execution/exfiltration path from the clone.
- **Image-import service-agent read boundary (post-exploitation).**
  `vmmigration.imageImports.create` makes the host-project service agent read the source Cloud
  Storage object. A known supported disk image readable by that service agent can therefore be
  materialized even if the API caller lacks `storage.objects.get`; output access in the target is
  still required.
- **AWS unattached-volume migration (post-exploitation, Preview).** The current alpha CLI and v1
  contract expose `CreateDiskMigrationJob` and `RunDiskMigrationJob`. They reuse
  `vmmigration.migratingVms.create` and `vmmigration.migratingVms.update`, respectively, and can
  materialize a selected unattached EBS volume as a Compute Engine Persistent Disk. An authorized
  AWS source, deployable target/service-agent boundary, and separate attacker access to the output
  disk remain prerequisites.

### Material corrections

- Removed nonexistent current CLI commands:
  `gcloud [alpha] migration vms clone-jobs ...`,
  `gcloud [alpha] migration vms sources ...`, and
  `gcloud [alpha] migration vms target-projects create ...`. Current local help exposes import
  workflows and target-project listing, so source/VM/job operations now use documented v1 REST.
- Corrected TargetProject location from a migration region to `global`.
- Corrected clone and target creation to LROs. The exact audit methods are
  `google.cloud.vmmigration.v1.VmMigration.CreateCloneJob` and
  `CreateTargetProject`, both Admin Activity and logged by default.
- Removed nonexistent `computeEngineTargetDefaults.serviceAccountScopes`; the current v1 schema
  contains `serviceAccount` but no scope field.
- Corrected the deputy boundary. VM Migration's host-project service agent, not the caller, owns the
  downstream Compute permissions. It needs `roles/vmmigration.serviceAgent` on the target and
  Service Account User on a selected target runtime service account. The console also asks the
  interactive configurator for Compute Viewer and Service Account User.
- Removed `compute.instances.*` from the minimum needed to start a clone. Target Compute
  operations are performed by the service agent; attacker access to the output is a separate
  prerequisite for disk inspection.
- Bounded clone contents to the latest successfully replicated snapshots rather than claiming an
  exact whole live VM or memory capture.
- Corrected the role statement: Admin and Viewer are the two user-facing predefined roles, but
  `roles/vmmigration.serviceAgent` is also a predefined role and must not be granted to humans.
- Documented the current Preview disk-migration surface rather than treating all disk commands as
  image-import aliases. Local alpha help confirms create/run/list use v1, target projects are
  global, and the audit contract deliberately maps disk jobs to the existing
  `vmmigration.migratingVms.*` permissions.

### Rejected or folded headings

- Folded “hijack where a migration lands” into clone post-exploitation. Redirecting target defaults
  is only an optional setup variant and additionally requires a registered, deployable target.
- Moved source/topology reads to enumeration. Secret fields are input-only; reads expose topology
  and non-secret identifiers, not stored VMware/AWS/Azure secrets.
- Removed deletion and operation cancellation from post-exploitation. They are destructive denial
  of service rather than sensitive-information acquisition.
- Removed “standing source/datacenter connector” persistence. A resource record alone is not a
  bridge; a usable connector needs an installed/registered appliance and external-source authority.
- Removed passive malicious-image persistence. An imported image does not execute until a separate
  actor intentionally launches from it, making the persistence claim speculative and duplicative.
- Folded durable target-default poisoning into the retained privesc/post techniques. It can affect a
  later operator-triggered job, but does not maintain IAM authorization after the attacker is
  revoked.

### Telemetry conclusions

- VM Migration mutating methods retained here are Admin Activity and LROs, normally producing start
  and completion entries. GET/LIST methods are Data Access with `ADMIN_READ` and are off by
  default.
- Compute instance/image/disk creation is downstream Admin Activity attributed to the VM Migration
  service agent. Metadata-server token reads do not generate Cloud Audit Logs.
- Cloud Storage `storage.objects.get` by the service agent is Data Access and off by default.
- Preview `CreateDiskMigrationJob` and `RunDiskMigrationJob` are Admin Activity LROs and logged by
  default; optional `FetchStorageInventory` is Data Access and off by default. AWS-side
  snapshot/read operations are outside Google Cloud Audit Logs.
- The official service audit catalog supports the VM Migration method/class/LRO claims. Downstream
  method emission and exact principal attribution should still be captured in a disposable live
  test before relying on a correlation as the only detector.

### Evidence limits

- No live migration estate was available for a no-residue test, and provisioning a source,
  replication appliance, replicated VM, and clone would be disproportionate to this documentation
  audit.
- The raw REST contract lists only `vmmigration.migratingVms.update` for patch and
  `vmmigration.cloneJobs.create` for clone creation. The console workflow performs extra
  target-resource visibility and Service Account User checks; a future least-privilege test should
  determine whether a raw API patch of metadata has any undocumented caller-side target checks.
- Startup scripts require a compatible guest environment and network path. They are not guaranteed
  to execute on every migrated source image.

## 2026-09-28 — independent reciprocal cross-review

- Re-opened the current v1 REST/audit contracts, target-project and target-service-account guides,
  image-import and Preview disk-migration guides, generated v1 client schemas, GA/alpha local CLI
  surfaces, and public predefined-role metadata. No project/customer cloud state was read or
  changed.
- Confirmed the retained raw permissions and exact VM Migration audit methods. In particular,
  `CreateDiskMigrationJob` and `RunDiskMigrationJob` currently exist in v1, use
  `vmmigration.migratingVms.create` and `vmmigration.migratingVms.update`, and are Admin Activity
  LROs. The installed disk-migration CLI is alpha under `gcloud migration vms` and calls v1; the
  official Preview how-to still contains stale `gcloud alpha compute migration` and v1alpha1
  examples.
- Confirmed every `TargetProject` reference used by the commands is under `locations/global`, while
  sources, migrating VMs, jobs, and imports are regional.
- Tightened the identity boundary: target VMs have no runtime service account by default. The
  host-project VM Migration service agent needs `iam.serviceAccounts.actAs` when one is selected;
  the documented console configurator also needs Service Account User, while the metadata-only raw
  patch contract itself lists only `vmmigration.migratingVms.update`. Arbitrary runtime-SA
  replacement is therefore not claimed by the retained primitive.
- Corrected downstream telemetry wording so `v1.compute.instances.insert` is the guaranteed VM
  creation signal and `v1.compute.disks.insert` is conditional on the service issuing a separate
  disk request rather than creating disks inline.
- Reconfirmed that image import reads the known object as the host-project VM Migration service
  agent, not the caller, and that output access remains a separate prerequisite. The current GA
  image-import declarative command sends `CreateImageImport` directly and does not add an implicit
  GET/poll method.
- Reconfirmed that removing all service-level persistence H3s is prudent: durable target-default
  poisoning is a delayed execution/data-exposure setup, connector records need a registered
  appliance and external authority, and passive images do not execute on their own.
