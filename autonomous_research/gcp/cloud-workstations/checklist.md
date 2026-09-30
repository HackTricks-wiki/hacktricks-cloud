# Cloud Workstations — research checklist

- [ ] When an authorized project already has the API enabled, compare normal `list` with both
      `listUsable` endpoints under minimal custom roles and confirm their negative audit evidence.
- [ ] Test whether config-level IAM inheritance plus `grantWorkstationAdminRoleOnCreate` creates any
      cross-user sharing path not already covered by the documented workstation policy-admin path.
- [ ] Inspect disk-assignment and shutdown platform-log payloads in a live, pre-existing deployment
      to map useful detection fields; do not create a cluster only for logging inspection.
- [ ] Re-check the stable v1 `SuspendWorkstation` surface as it moves out of v1beta and determine
      whether it adds anything beyond the already documented availability/cost controls.
- [ ] Determine whether `workstationClusters.update` can turn `workstationAuthorizationUrl` into a
      practical victim-token interception path, or only a generic phishing redirect. The redirect
      supplies workstation/hostname state but no credential, so do not publish without proving a
      token-bearing browser flow and its minimum prerequisites.
