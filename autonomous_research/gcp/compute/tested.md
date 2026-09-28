
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
