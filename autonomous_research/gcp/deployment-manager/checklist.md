# Deployment Manager — future test checklist

Last updated: 2026-09-28

## Safe expected-functionality validation

- [ ] Use only an eligible disposable project where Deployment Manager is already enabled and has
      prior deployments; do not attempt to create new-customer eligibility after the June 30, 2026
      cutoff.
- [ ] Give a test principal only `deploymentmanager.deployments.create`, create a harmless VM whose
      startup script reports only the attached service-account email, and capture the initiating
      `v2.deploymentmanager.deployments.insert` plus downstream `v1.compute.instances.insert`
      principals. Do not retrieve or retain an OAuth token for the documentation test.
- [ ] Repeat with only `.update`, an existing synthetic deployment, a supplied fingerprint and a
      complete configuration that preserves every fixture resource. Compare raw REST, gcloud
      `--async`, and synchronous helper permissions. Current local SDK source shows that update
      still reads the deployment before and after the mutation even with a supplied fingerprint.
- [ ] Test a hardened Google APIs Service Agent missing `iam.serviceAccounts.actAs`, then restore its
      exact original policy. Confirm the downstream attachment fails without weakening production.
- [ ] Capture LRO start/completion linkage, deployment operation reads, Compute operation telemetry,
      the separate `iam.serviceAccounts.actAs` event, receiver/network evidence and cleanup events.
- [x] Confirm deployment-level IAM enforcement. A direct `roles/deploymentmanager.admin` binding to
      a no-project-role service account allowed HTTP 200 on the exact deployment; policy write was
      `v2.deploymentmanager.deployments.setIamPolicy`. The policy, deployment, bucket, account and API
      state were restored or deleted.
- [ ] Delete the deployment and every created VM, disk, address, firewall/network resource and local
      test file. Restore any service-agent IAM policy exactly and confirm Cloud Asset/IAM searches
      contain no fixture names.

## Manifest disclosure

- [ ] Deploy synthetic credentials in four shapes: a recognized scalar credential property, a
      template/import, a YAML map and a YAML list. Retrieve the manifest with a one-permission
      principal and record precisely which copies are redacted.
- [ ] Compare direct known-manifest GET with discovery through deployment/manifest lists while Data
      Access audit logging is off and on. Delete the deployment and synthetic values afterward.

## Potential vulnerability probes — keep private if successful

- [ ] In an eligible disposable project, register a type provider pointing only to controlled public,
      redirect, unroutable RFC 5737 and approved internal-test endpoints. Measure DNS, redirect,
      scheme, IP-range and response-disclosure behavior without targeting metadata or third parties.
- [ ] Test URL parser disagreement using harmless encodings, redirects and IPv4/IPv6 textual forms.
      A real internal reachability or credential-forwarding boundary failure is a private report,
      not an expected HackTricks technique.
- [ ] Test whether deployment-level IAM also accepts and enforces a purpose-built custom role
      containing only `.update`; the predefined Admin binding is confirmed, but a one-permission
      custom role would establish the narrowest grant path.
