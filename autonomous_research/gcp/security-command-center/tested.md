# Security Command Center — tested

Security Command Center (SCC). Covered (config-tamper post-ex, Security Posture tamper persistence).

## CRITICAL correction applied (do NOT regress)
- `SetMute`, `SetFindingState`, `UpdateFinding`, `BulkMuteFindings`, `Create/Update/DeleteNotificationConfig`
  are **DATA_WRITE (off by default), NOT ADMIN_WRITE** — inverted the stealth story (muting + severing
  the Pub/Sub SIEM feed = no audit trail by default). Mute-config CRUD, BigQuery-export CRUD, source
  `SetIamPolicy` are correctly ADMIN_WRITE. `sources.setIamPolicy` also in `securitycenter.sourcesAdmin`.

## Standing item (REST-only)
- `integratedvulnerabilityscannersettings` / `rapidvulnerabilitydetectionsettings` — REST-only, deferred.

## 2026-09-28 post-exploitation audit

Documentation-only verification against current Google Cloud primary documentation and the installed
`gcloud scc` help; no SCC resources or APIs were changed.

- Revalidated the audit split: Security Center Management service/module writes, mute-config CRUD,
  BigQuery-export CRUD, and source `SetIamPolicy` are Admin Activity. Direct/bulk mute, finding
  state/update, and notification-config CRUD are Data Access (`DATA_WRITE`) and off by default.
- Corrected mute semantics: muted findings remain queryable and still contribute to the Compliance
  page/reports. Pub/Sub also continues exporting new or updated muted findings unless its filter
  explicitly excludes `mute="MUTED"`.
- Replaced the nonexistent `gcloud scc findings set-state` command with the v2 REST `:setState`
  operation (`securitycenter.findings.setState`) and documented the distinct gcloud
  `findings update --state=INACTIVE` path (`securitycenter.findings.update`).
- Corrected continuous-export scope to project/folder/organization and location-aware v2 resources.
  Export changes only affect future delivery; existing Pub/Sub messages, BigQuery rows, and downstream
  copies are not recalled.
- Reduced custom-module coverage to deletion of a real ETD/SHA custom module. Removed the speculative
  low-value no-op-module claim and documented exact delete permissions and owning-parent constraint.
- Corrected source-IAM escalation: `sources.setIamPolicy` is organization-source authority. A Sources
  Admin can grant `findingsEditor` on that source, but this is not possible "without org-level SCC
  authorization". Policy merge must preserve bindings and `etag`.
- Removed detector-specific bypass recipes and unstable module counts. Replaced them with documented
  coverage boundaries: ETD receives an independent internal duplicate flow stream when customer VPC
  Flow Logs are off; VMTD encryption/filesystem restrictions apply to disk scanning, while
  Confidential/Arm limitations apply to VMTD generally; GKE Sandbox is outside CTD support.
- Confirmed current gcloud syntax locally for service updates, individual/bulk mute, finding update,
  notification/BQ export deletion, and ETD/SHA custom-module deletion. Module YAML uses
  `intended_enablement_state`; custom-module delete has no separate `--location` flag.

Primary references used: SCC API audit logging, Security Center Management API audit logging, mute
findings/individual findings, continuous Pub/Sub and BigQuery exports, ETD log activation requirements,
CTD use requirements, VMTD limitations, custom-module documentation, and source IAM API/sample pages.

## 2026-09-28 independent-review corrections

- Made audit-query scope explicit: read logs at the project, folder, or organization that owned the
  write rather than assuming a child-project query includes parent-scoped SCC activity.
- Qualified detector disablement for batch scanners: an already-running scan can finish and emit
  findings before the new setting takes effect.
- Bounded manual `INACTIVE` durability by detector class. Threat-finding state is not automatically
  changed, while some vulnerability/misconfiguration services manage state and can reactivate a
  finding while its condition persists.
- Added mute edge cases: SCC error findings are not mutable, and muting a toxic-combination finding
  leaves it active but closes its case; a case is also closed when all of its findings are muted.
- Split notification-config and BigQuery-export tampering because their audit contracts and stealth
  differ: notification writes are off-default `DATA_WRITE` (Medium), whereas BigQuery export writes
  are always-on `ADMIN_WRITE` (Low).
- Documented that ETD/SHA custom-module deletion cannot be recovered and restoration requires
  recreating the module.
- Hardened the source-IAM example by requesting policy version 3, preserving `version`/`etag`, and
  extending only an unconditional `findingsEditor` binding; otherwise it appends a new binding.
- Restored one bounded runtime-coverage technique: GKE Sandbox is outside CTD, Confidential/Arm VMs
  are outside VMTD, and CSEK/CMEK or unsupported file systems exclude only VMTD disk scanning. The
  page explicitly retains Kubernetes/Compute audit visibility and other detector coverage.
