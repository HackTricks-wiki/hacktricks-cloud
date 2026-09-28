# Compute Engine — post-exploitation audit

## 2026-09-28 — permissions, impact, stealth, and telemetry review

- Audited all 26 retained Compute/VPC post-exploitation sections against current official Google
  Cloud documentation. Added a concise minimum-permission/prerequisite boundary and categorical
  stealth rating to each technique; preserved an expandable log table for every section.
- Corrected Compute reads: `instances.getGuestAttributes` and `instances.getSerialPortOutput` are
  `DATA_READ` events, not unauditable calls. They are silent under the default audit configuration
  but become caller-attributed when Compute Data Access logging is enabled.
- Corrected interactive serial-console telemetry: the metadata write is Admin Activity and the
  gateway emits `google.ssh-serialport.v1.connect`/`.disconnect` records. Documented the attached-SA
  `actAs` requirement, Linux port 1, Windows port 2, and the guest-local login requirement.
- Corrected storage boundaries: zonal standard snapshots check `compute.disks.createSnapshot` plus
  destination `compute.snapshots.create`; instant-snapshot insertion also checks source
  `compute.disks.useReadOnly`; attachment and image/snapshot conversions have separate source-use
  and destination-create permissions. In-guest filesystem reads are not Cloud API Data Access calls.
- Corrected anti-recovery commands: an attached snapshot schedule must be detached before deletion,
  and early recycle-bin purge uses `gcloud beta compute recoverable-snapshots delete`, not the
  nonexistent `snapshots delete --recoverable=false` flag.
- Narrowed two overstated network techniques. Alias IP assignment can claim only an unused range, so
  it cannot steal a live Pod/service IP. Cloud Router advertisements affect what BGP peers send
  toward Google Cloud and do not alone create an attacker-controlled next hop or transparent MITM.
- Documentation-only pass. No cloud resource was created or modified.
