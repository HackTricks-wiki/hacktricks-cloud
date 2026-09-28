# Backup and DR - open research checklist

- [ ] With explicit approval for a live test, verify whether a restored Compute VM request that
  supplies instance metadata or a service account performs any additional caller-side authorization
  checks beyond the two permissions documented for CLI/API restore.
- [ ] With explicit approval and disposable clusters, capture the exact GKE/Kubernetes audit events
  emitted when the Backup for GKE agent reads Secret objects and when it writes them during restore.
- [ ] Revisit cross-project GKE backup/restore after the standard backup-plan guide removes its stale
  same-project-only sentence; the dedicated cross-project guides and release notes describe the GA
  channel workflow.
- [ ] Monitor new Backup and DR workload types for restore methods that expose credentials or data
  through a stronger service identity.
