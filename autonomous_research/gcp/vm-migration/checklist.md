# VM Migration research checklist

## Completed

- [x] Inspect current v1 discovery resource and request schemas.
- [x] Inspect local GA/alpha `gcloud migration vms` command coverage.
- [x] Verify Admin, Viewer, and service-agent predefined role contents/stages.
- [x] Separate caller, host-project service-agent, runtime-service-account, target-project, and
  source-bucket permission boundaries.
- [x] Correct TargetProject global location and clone/image import request syntax.
- [x] Verify exact VM Migration audit methods, classes, LRO status, and default visibility.
- [x] Consolidate clone/redirection into one bounded post-exploitation primitive.
- [x] Move topology reads to enumeration and remove destructive DoS from post-exploitation.
- [x] Reject connector-record and passive-image persistence overclaims.
- [x] Review Preview AWS disk migration, verify alpha CLI syntax, permission reuse, exact audit
  methods/classes/LRO status, and retain it as a bounded post-exploitation primitive.
- [x] Independently cross-review current v1 versus stale Preview-guide v1alpha1/old CLI examples.
- [x] Recheck default runtime-SA behavior and separate caller-console, host-service-agent, and target
  runtime identity boundaries.
- [x] Bound downstream Compute logging to guaranteed instance/image/disk effects and conditional
  helper requests rather than assuming every workflow emits a standalone disk insert.

## Safe future validation

- [ ] In synthetic host/target projects, create a harmless source VM with a privileged-looking but
  synthetic runtime service account. Test raw metadata-only `UpdateMigratingVm` as a principal
  lacking caller-side `iam.serviceAccounts.actAs`, while the VM Migration service agent has it.
  Capture the exact allow/deny boundary and delete the clone immediately.
- [ ] Capture both LRO entries for `UpdateMigratingVm`, `CreateCloneJob`, and
  `CreateImageImport`, plus downstream Compute entries and exact service-agent principal.
- [ ] With synthetic VMDK data, grant object read only to the VM Migration service agent and verify
  whether an image-import caller without Storage permissions can import the known object. Remove
  the output image, import resource, IAM binding, and source object immediately.
- [ ] Verify which OAuth scopes VM Migration assigns when a target runtime service account is
  selected; bound metadata-token impact to those observed scopes.
- [ ] Test Linux and Windows startup metadata only on synthetic images with the appropriate guest
  environment, then remove target-default metadata and every clone.
- [ ] Confirm whether adding a TargetProject through raw REST modifies target-project IAM or merely
  registers the resource when the caller lacks target `resourcemanager.projects.setIamPolicy`.
  Do not test against a non-disposable target.
- [ ] Review newer machine-image-import and deployment resources for a distinct service-agent
  confused-deputy boundary as their audit documentation matures.
- [ ] In a disposable AWS/GCP lab, migrate a synthetic unattached EBS volume and capture the two VM
  Migration LRO entries, downstream `v1.compute.disks.insert`, AWS-native snapshot/read events, and
  cleanup behavior. Delete the target disk, migration job, source volume/snapshot, and test grants.
