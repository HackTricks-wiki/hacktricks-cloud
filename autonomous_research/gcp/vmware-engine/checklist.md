# VMware Engine — research checklist

Last reviewed: 2026-09-28

## Completed

- [x] Reconcile current `show*Credentials`, `reset*Credentials`, IAM-policy, and operation schemas.
- [x] Verify current predefined-role membership for credential and policy permissions.
- [x] Correct the CloudOwner boundary from unrestricted Administrator to documented
      `Cloud-Owner-Role`.
- [x] Reconcile Cloud Audit classifications/defaults and the separate appliance-syslog plane.
- [x] Replace the nonexistent private-cloud IAM gcloud command with a policy-preserving REST flow.
- [x] Remove the guest-credential contradiction from the VMware Tools claim.
- [x] Remove destructive-only, duplicate persistence, invalid CLI, and fragile raw-VMDK claims.
- [x] Add exact prerequisites, impact, categorical stealth, and expandable telemetry tables to every
      retained privilege-escalation and post-exploitation technique.
- [x] Complete focused shell, Markdown, reference, URL, local-link, and diff validation without a
      cloud mutation.

## Safe future validation

- [ ] On a disposable private cloud with synthetic VMs, test `show*Credentials` under minimum
      custom roles with VMware Engine Data Access logging disabled/enabled; record exact request and
      response redaction without retaining the passwords.
- [ ] In that disposable environment, change a generated password inside the appliance, confirm
      the stale-show boundary, then test reset followed by show. Restore the expected credential and
      remove all temporary principals immediately.
- [ ] Test a private-cloud resource-level `roles/vmwareengine.admin` grant using a custom principal
      that has only `getIamPolicy`/`setIamPolicy`; preserve and restore the exact original policy.
- [ ] With a synthetic VM and isolated datastore/folder, validate clone/offline-read operations and
      enumerate exact vCenter events, syslog records, and guest-telemetry absence. Delete the clone
      and snapshots immediately.
- [ ] With synthetic NSX segments/flows, make one reversible firewall/routing change and compare
      local appliance audit, forwarded NSX syslog, DFW logs, flow visibility, and Cloud Audit Logs.
- [ ] Investigate whether unconsumed HCX activation keys expose a high-value post-exploitation or
      cross-environment trust primitive; do not publish until one-time-use and authority boundaries
      are demonstrated.

## Guardrails for future live work

- Use only a disposable private cloud and synthetic workloads; never clone, snapshot, inspect, or
  reroute production data.
- Snapshot/export every relevant appliance configuration and record every object created before a
  test; restore policies/routes/rules and verify inventory afterward.
- Avoid password reset unless the test includes a confirmed restoration path and no human/operator
  session depends on the current credential.
- Never use private-cloud/cluster deletion, delete-now, destructive datastore operations, or broad
  allow-any rules.
- Remove VM clones, snapshots, temporary vCenter/NSX identities, IAM bindings, routes, NAT rules,
  firewall rules, external addresses, and logging changes before closing a test.
