# AWS Deadline Cloud — open ideas

- [x] CreateQueue/UpdateQueue + PassRole -> AssumeQueueRoleForUser full-role vend (privesc) — DONE,
  VERIFIED live. See tested.md.
- [x] **Fleet-role privesc parallel** — DONE, VERIFIED live. AssumeFleetRoleForWorker vends the FULL
  (un-narrowed) fleet role; a Customer-Managed Fleet + logical CreateWorker needs NO compute. See
  tested.md. Documented as a companion privesc on the enum page.
- [ ] **CreateMonitor `--role-arn` + identityCenterApplicationArn** — Monitor wires an Identity Center
  app; check whether the monitor role or the IC app is abusable (needs IC, not in member acct).
- [ ] **jobRunAsUser / job attachments** — a submitted job runs on workers as the queue role; if you can
  submit jobs to a privileged queue (CreateJob), the job payload executes with queue-role creds on the
  worker (RCE-as-role). Needs a fleet+worker (compute cost) to test end-to-end.
