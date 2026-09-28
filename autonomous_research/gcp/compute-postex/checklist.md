# Compute Engine post-exploitation checklist

## Completed 2026-09-28

- [x] Inventory every level-three technique heading (26 retained).
- [x] Add explicit Potential Impact, minimum permissions/prerequisites, categorical Stealth, and an
      expandable Logs generated table to every retained technique.
- [x] Reconcile Compute read/write audit classes and default visibility with the official audit
      method catalog.
- [x] Reconcile image, snapshot, instant-snapshot, disk, and VM-attachment permission boundaries.
- [x] Reconcile Packet Mirroring, static route, Cloud Router/NAT/BGP, Cloud Armor, CDN, URL map,
      external-IP, flow-log, and alias-IP semantics.
- [x] Reconcile Shielded VM, availability, anti-recovery, guest-attribute, and serial-console claims.
- [x] Correct commands that referenced nonexistent flags or invalid operation ordering.
- [x] Use only official Google Cloud references; no cloud resources touched.

## Future live validation candidates

- [ ] With a disposable workload, verify the exact request-body fields retained/redacted for CDN
      signed-key changes and each Cloud Armor bulk-import variant; do not record key material.
- [ ] With a disposable Network Management flow-log config, capture the current fully-qualified
      update/delete method names and resource labels, then tear down all test configuration.
- [ ] With Data Access logging temporarily enabled in an authorized disposable project, capture one
      `getGuestAttributes` and one `getSerialPortOutput` entry and then restore the prior audit policy.
