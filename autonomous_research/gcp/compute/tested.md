
## compute.instantSnapshots (GA 2024) — annotated (not a new technique)
Zero prior wiki mention, but Instant Snapshots are the same disk-data-copy exfil family as the
documented regular-snapshot exfil (same-region, on-disk storage; cross-project exfil still routes
through a standard snapshot/disk/image conversion). Added a NOTE to the snapshot setIamPolicy exfil
section on gcp-compute-post-exploitation.md flagging compute.instantSnapshots.create /
.setIamPolicy as a distinct, faster/stealthier permission achieving the documented outcome — not a
new exfil path, so a note not a section (no-duplicate bar).

## 2026-09-28 — Compute privilege-escalation page audit (official-doc validation only)

Scope: every technique-like section in
`gcp-privilege-escalation/gcp-compute-privesc/README.md`. No cloud resources or APIs were touched in
this pass.

Results:

- Added explicit categorical stealth ratings to 15 real technique sections. No technique was rated
  impossible to detect: OS Config and guest-local exploitation are high-stealth, while each still
  has API-state, agent, guest, or subsequent credential-use detection opportunities.
- Removed the standalone `Bypass Access Scopes` placeholder. Its useful content is now folded into
  `compute.instances.setMetadata` and `compute.instances.setServiceAccount`; the supported route is
  a logged `setServiceAccount --scopes=cloud-platform`, not a demonstrated scope bypass.
- Corrected OS Login telemetry: login attempts use OS Login data-plane records, signed SSH keys are
  Data Access, several profile/key methods are explicitly unaudited, and OS Login does not publish
  keys through Compute metadata.
- Corrected direct VM/MIG run-as-SA impact from “full control of the SA” to renewable short-lived
  token access bounded by effective IAM, conditions, scopes, organization policy, VPC Service
  Controls, and service controls.
- Corrected MIG authorization: Compute documents the Google APIs Service Agent as the principal
  performing MIG operations and validates its Service Account User/resource access. Both new-MIG
  and existing-MIG permission lists now include configuration-dependent VM/template permissions.
- Replaced the invalid `instance-templates create --source-instance-template` example with a working
  explicit-template reconstruction flow and documented the console `Create similar` alternative.
- Corrected VM Manager scope to eligible running VMs with an active OS Config agent and documented
  private-GCS script read requirements plus exact Data Access method names.
- Corrected machine-image/snapshot/disk IAM impact: resource IAM does not stream disk bytes and all
  paths require follow-on target-project creation/attachment permissions. Snapshot creation uses
  `compute.disks.createSnapshot` on the source plus project-level `compute.snapshots.create`.
- Corrected Windows requirements (`instances.get`, metadata fingerprint, account-manager enabled,
  reachable management path) and moved the Linux OS Login-disable path to general metadata abuse.
- Corrected the global “reads are not logged” statement to “not logged by default”; Compute reads
  are Data Access methods.

## 2026-09-28 — end-to-end Compute enum/privesc/post-exploitation/persistence audit

Scope: the Compute enum page and the dedicated privilege-escalation, post-exploitation and
persistence pages. This was an official-documentation, local CLI-help and predefined-role review;
no GCP resources were created, modified or deleted.

Retained high-value coverage:

- 15 privilege-escalation H3s. Added explicit minimum-permission/prerequisite blocks to every H3,
  including helper-read/fingerprint permissions, external-user OS Login, condition/etag-safe
  instance IAM merge, caller-versus-Google-APIs-Service-Agent MIG checks, and target-VM-SA access
  to private OS Config scripts.
- 23 post-exploitation H3s after applying the no-garbage bar. Existing read/write audit categories,
  bounded network/storage effects and downstream signals were rechecked against the current
  Compute audit catalog and current CLI surface.
- 4 persistence H3s: instance/project startup metadata, custom-image-family poisoning, existing-MIG
  template replacement, and recurring VM Manager patch deployment. These are recurring execution
  or self-healing paths rather than merely long-lived resources.
- Enum corrections separate machine images from custom images, remove the unrelated container-image
  command and duplicate export workflow, make disk IAM location explicit, and state the current
  Compute/OS Config Data Access defaults.

Rejected or folded hypotheses:

- **Create a VM with a privileged attached SA as persistence** — retained only in privesc. VM
  creation is a run-as-SA boundary crossing, but a plain long-lived VM is not a distinct recurring
  persistence mechanism without a startup, image, group, or scheduled execution path.
- **Backdoor a snapshot lineage** — replaced by the bounded image-family technique. A snapshot is a
  point-in-time source; it does not propagate a modified filesystem to future consumers unless an
  attacker performs and wins a separate disk/image/template workflow.
- **`compute.urlMaps.invalidateCache` as post-exploitation** — rejected as availability/cost-only.
  The useful research result remains: `v1.compute.urlMaps.invalidateCache` is always-on Admin
  Activity and records host/path, but it yields no foothold, secret or boundary crossing.
- **Standalone VM reset/stop/simulated-maintenance/delete-access-config heading** — rejected as a
  destructive/availability grab bag. Each method is default-on Compute Admin Activity; simulated
  maintenance impact is configuration-dependent rather than guaranteed.
- **Snapshot schedule/snapshot/image deletion anti-recovery heading** — rejected as destructive-only
  for this page. `removeResourcePolicies`, schedule deletion and GA snapshot/image deletions are
  default-on Admin Activity; the Preview recoverable-snapshot purge remained unverified and is not
  promoted as a book technique.

Telemetry correction retained for future tests: `CreatePatchDeployment` and direct
`ExecutePatchJob` are VM Manager Data Access `DATA_WRITE`, disabled by default, and neither is an
LRO. A recurring deployment creates patch-job/service state, but official audit documentation does
not promise that a service-triggered scheduled run emits the same caller-attributed
`ExecutePatchJob` record. Do not claim that row without tenant evidence.

Reciprocal review corrected six additional precision edges. Project common metadata unconditionally
requires project-scoped `iam.serviceAccounts.actAs`, while raw `instances.setMetadata` lists only
the instance write permission; connection/password helpers can impose separate checks. OS Login's
SSH-auditing guide names `CheckPolicy`, `StartSession`, and `ContinueSession`, but the current audit
catalog does not classify their log type/default availability, so only `SignSshPublicKey` retains a
published Data Access classification. The regional-disk IAM example now uses REST because the
gcloud helper accepts only `--zone`; IAM helper read permissions, a full VM-create example, and
metadata-value redaction wording were also fixed.
