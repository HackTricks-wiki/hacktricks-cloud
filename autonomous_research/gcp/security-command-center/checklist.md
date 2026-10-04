# Security Command Center — open ideas

Open ideas — Security Command Center.

- (none open) — mute-config/notification/bqexport/detector-disable defense-evasion AND scanner-as-recon are ALREADY documented (`gcp-security-command-center-enum.md` + web-security-scanner enum). Coverage sweep found nothing meaningful missing. Verified duplicate → nothing to ship.

## Open verification leads (2026-09-28)

- [x] Reduce the privilege-escalation page to the one SCC-specific source-policy transition and remove generic IAM/defense-evasion duplicates.

- In a disposable SCC Premium test hierarchy, verify the least-privilege custom roles and actual audit entries for project/folder service overrides and module-only service updates. Documentation currently provides the exact permissions and classes; no live mutation was authorized for this audit.
- With SCC Data Access audit logging explicitly enabled in a disposable project, capture v2 regional `SetMute`, `BulkMuteFindings`, `SetFindingState`, `UpdateFinding`, and notification-config entries, including long-running-operation metadata and exact resource names.
- Test continuous-export timing for mute and state updates and destination-side permission failures, without modifying a production defender pipeline.
- Revisit the existing REST-only `integratedvulnerabilityscannersettings` and `rapidvulnerabilitydetectionsettings` lead when their management/audit contracts are fully documented.
- In a disposable organization source containing both conditional and unconditional IAM bindings, verify that the version-3 read/merge/write example preserves conditions and rejects stale `etag`s without modifying a production source policy.
- In an authorized disposable GKE/Compute environment, capture the exact Kubernetes Pod-create and Compute instance-insert audit entries for the documented CTD/VMTD unsupported-runtime cases, and separately confirm that encrypted-disk placement excludes only the VMTD disk-scanning detector.
