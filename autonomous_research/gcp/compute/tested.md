
## 2026-10-04 — recoverable-snapshot IAM escalation and deleted-data recovery

Live-tested the September 2026 Compute Engine snapshot recycle-bin Preview in `gcp-labs-eqd4ny8d` with a blank 10 GB disk, standard snapshot, disposable service account, exact custom role, and isolated gcloud configuration.

Confirmed:

- The system effective rule retained standard snapshots for three days. Deleting the active snapshot removed it from `gcloud compute snapshots list` and created a generated recoverable-snapshot resource visible only through the beta inventory.
- Resource IAM on the active snapshot did not carry into the recoverable tombstone. A caller that had Storage Admin only on the active snapshot was denied recoverable get and recover after deletion.
- A caller with only project-level `compute.recoverableSnapshots.setIamPolicy` could blindly replace the known tombstone's IAM policy and grant itself `roles/compute.storageAdmin`. It then read and recovered the tombstone without having started with recover, get, ordinary snapshot-IAM, snapshot-use, or disk-data permissions.
- The recovered active snapshot inherited the IAM policy written on the tombstone. It received a new name/time and did not regain the synthetic `ht-test` label.
- Repeating the tombstone self-grant after deleting the restored snapshot allowed the reduced caller to invoke `recoverableSnapshots.delete`, irreversibly removing it before expiry.
- Successful `beta.compute.recoverableSnapshots.setIamPolicy`, `.recover`, and `.delete` calls were always-on Admin Activity. The policy body and requested recovery name were recorded; denied probes were also logged. Read/list visibility remains Data Access and off by default.

Rejected/bounded hypotheses:

- Deleting an attacker-readable active snapshot is not resource-IAM persistence by itself because the active policy did not survive into the tombstone.
- The feature is not an arbitrary data-read vulnerability: recovery and permanent deletion are expected consequences of the published permissions. Reading the recovered bytes still needs snapshot use, destination resource creation/attachment or export, and any CMEK access.
- No private report was opened. The useful result is the exact single-permission self-grant path and the inventory/detection blind spot.

Cleanup:

- Permanently deleted both generated recoverable snapshots, the restored/active snapshot, and the blank source disk.
- Deleted the disposable key and service account, removed both project bindings, deleted the custom role, and securely removed `/tmp/ht-recycle-auth-1004`.
- Verified `disk=0 snapshot=0 recoverable=0 sa=0 bindings=0 cred_dir=no`. The custom role remains only as GCP's normal soft-deleted tombstone. Compute API was enabled before testing and remains enabled.

## compute.instantSnapshots (GA 2024) — annotated (not a new technique)
Zero prior wiki mention, but Instant Snapshots are the same disk-data-copy exfil family as the documented regular-snapshot exfil (same-region, on-disk storage; cross-project exfil still routes through a standard snapshot/disk/image conversion). Added a NOTE to the snapshot setIamPolicy exfil section on gcp-compute-post-exploitation.md flagging compute.instantSnapshots.create / .setIamPolicy as a distinct, faster/stealthier permission achieving the documented outcome — not a new exfil path, so a note not a section (no-duplicate bar).

## 2026-09-28 — Compute privilege-escalation page audit (official-doc validation only)

Scope: every technique-like section in `gcp-privilege-escalation/gcp-compute-privesc/README.md`. No cloud resources or APIs were touched in this pass.

Results:

- Added explicit categorical stealth ratings to 15 real technique sections. No technique was rated impossible to detect: OS Config and guest-local exploitation are high-stealth, while each still has API-state, agent, guest, or subsequent credential-use detection opportunities.
- Removed the standalone `Bypass Access Scopes` placeholder. Its useful content is now folded into `compute.instances.setMetadata` and `compute.instances.setServiceAccount`; the supported route is a logged `setServiceAccount --scopes=cloud-platform`, not a demonstrated scope bypass.
- Corrected OS Login telemetry: login attempts use OS Login data-plane records, signed SSH keys are Data Access, several profile/key methods are explicitly unaudited, and OS Login does not publish keys through Compute metadata.
- Corrected direct VM/MIG run-as-SA impact from “full control of the SA” to renewable short-lived token access bounded by effective IAM, conditions, scopes, organization policy, VPC Service Controls, and service controls.
- Corrected MIG authorization: Compute documents the Google APIs Service Agent as the principal performing MIG operations and validates its Service Account User/resource access. Both new-MIG and existing-MIG permission lists now include configuration-dependent VM/template permissions.
- Replaced the invalid `instance-templates create --source-instance-template` example with a working explicit-template reconstruction flow and documented the console `Create similar` alternative.
- Corrected VM Manager scope to eligible running VMs with an active OS Config agent and documented private-GCS script read requirements plus exact Data Access method names.
- Corrected machine-image/snapshot/disk IAM impact: resource IAM does not stream disk bytes and all paths require follow-on target-project creation/attachment permissions. Snapshot creation uses `compute.disks.createSnapshot` on the source plus project-level `compute.snapshots.create`.
- Corrected Windows requirements (`instances.get`, metadata fingerprint, account-manager enabled, reachable management path) and moved the Linux OS Login-disable path to general metadata abuse.
- Corrected the global “reads are not logged” statement to “not logged by default”; Compute reads are Data Access methods.

## 2026-09-28 — end-to-end Compute enum/privesc/post-exploitation/persistence audit

Scope: the Compute enum page and the dedicated privilege-escalation, post-exploitation and persistence pages. This was an official-documentation, local CLI-help and predefined-role review; no GCP resources were created, modified or deleted.

Retained high-value coverage:

- 15 privilege-escalation H3s. Added explicit minimum-permission/prerequisite blocks to every H3, including helper-read/fingerprint permissions, external-user OS Login, condition/etag-safe instance IAM merge, caller-versus-Google-APIs-Service-Agent MIG checks, and target-VM-SA access to private OS Config scripts.
- 23 post-exploitation H3s after applying the no-garbage bar. Existing read/write audit categories, bounded network/storage effects and downstream signals were rechecked against the current Compute audit catalog and current CLI surface.
- 4 persistence H3s: instance/project startup metadata, custom-image-family poisoning, existing-MIG template replacement, and recurring VM Manager patch deployment. These are recurring execution or self-healing paths rather than merely long-lived resources.
- Enum corrections separate machine images from custom images, remove the unrelated container-image command and duplicate export workflow, make disk IAM location explicit, and state the current Compute/OS Config Data Access defaults.

Rejected or folded hypotheses:

- **Create a VM with a privileged attached SA as persistence** — retained only in privesc. VM creation is a run-as-SA boundary crossing, but a plain long-lived VM is not a distinct recurring persistence mechanism without a startup, image, group, or scheduled execution path.
- **Backdoor a snapshot lineage** — replaced by the bounded image-family technique. A snapshot is a point-in-time source; it does not propagate a modified filesystem to future consumers unless an attacker performs and wins a separate disk/image/template workflow.
- **`compute.urlMaps.invalidateCache` as post-exploitation** — rejected as availability/cost-only. The useful research result remains: `v1.compute.urlMaps.invalidateCache` is always-on Admin Activity and records host/path, but it yields no foothold, secret or boundary crossing.
- **Standalone VM reset/stop/simulated-maintenance/delete-access-config heading** — rejected as a destructive/availability grab bag. Each method is default-on Compute Admin Activity; simulated maintenance impact is configuration-dependent rather than guaranteed.
- **Snapshot schedule/snapshot/image deletion anti-recovery heading** — rejected as destructive-only for this page. `removeResourcePolicies`, schedule deletion and GA snapshot/image deletions are default-on Admin Activity; the Preview recoverable-snapshot purge remained unverified and is not promoted as a book technique.

Telemetry correction retained for future tests: `CreatePatchDeployment` and direct `ExecutePatchJob` are VM Manager Data Access `DATA_WRITE`, disabled by default, and neither is an LRO. A recurring deployment creates patch-job/service state, but official audit documentation does not promise that a service-triggered scheduled run emits the same caller-attributed `ExecutePatchJob` record. Do not claim that row without tenant evidence.

Reciprocal review corrected six additional precision edges. Project common metadata unconditionally requires project-scoped `iam.serviceAccounts.actAs`, while raw `instances.setMetadata` lists only the instance write permission; connection/password helpers can impose separate checks. OS Login's SSH-auditing guide names `CheckPolicy`, `StartSession`, and `ContinueSession`, but the current audit catalog does not classify their log type/default availability, so only `SignSshPublicKey` retains a published Data Access classification. The regional-disk IAM example now uses REST because the gcloud helper accepts only `--zone`; IAM helper read permissions, a full VM-create example, and metadata-value redaction wording were also fixed.

## 2026-09-28 - dedicated SSH-metadata page rebuild

Scope: every technique-like H3 in `gcp-privilege-escalation/gcp-compute-privesc/gcp-add-custom-ssh-metadata.md`. This pass used current official Compute Engine SSH-key, guest-agent, metadata, SSH-hardening, and audit documentation plus local Google Cloud CLI 586.0.0 help/source. No VM, metadata, IAM policy, SSH key in GCP, or other cloud resource was created, changed, or deleted. No cleanup was necessary. One read-only `roles/file.editor` description was issued for the parallel Filestore audit; it did not affect this Compute result.

Retained results:

- One per-instance primitive: `compute.instances.setMetadata`, bounded to the selected eligible VM. The shown `gcloud ... instances add-metadata` merge also performs `instances.get`; the raw API command then calls `zoneOperations.wait`. Its helpers therefore require `compute.instances.get` and `compute.zoneOperations.get`; the raw API permission remains only the documented write permission when the fingerprint and full value are already known and the caller does not poll.
- One project primitive: `compute.projects.setCommonInstanceMetadata` plus the documented project-scoped `iam.serviceAccounts.actAs`. The shown `gcloud ... project-info add-metadata` merge performs `projects.get` and `globalOperations.wait`, adding `compute.projects.get` and `compute.globalOperations.get`.
- Both require metadata-based SSH, compatible guest-agent account management, a private key, and a reachable SSH path. OS Login, `block-project-ssh-keys`, custom guest behavior, and network controls bound the result.
- Both are Low stealth: the writes are default-on Admin Activity `ADMIN_WRITE`; helper reads are Data Access `ADMIN_READ` and off by default, including the operation waits; metadata values are redacted; direct SSH is guest and optional network telemetry rather than a Compute API event.

Pruned results:

- The overview H3 was explanatory text, not a technique.
- "existing privileged user" and "create a new privileged user" were duplicate uses of the same instance metadata write. Their useful username/key examples were merged into the retained H3.
- Unbounded claims of automatic project takeover were replaced with the eligible-VM and attached-SA IAM/access-scope boundary.

## 2026-09-28 reciprocal review of SSH metadata

Independently rechecked both retained headings against the current REST IAM sections, SSH-key and guest-agent documentation, Compute audit catalog, Google Cloud CLI 586.0.0 help, and local CLI source. The raw/CLI permission split, fingerprints, project-level `actAs`, eligible-VM bounds, commands, and telemetry remain accurate; no page correction was necessary. No cloud API or VM was accessed or changed.
