# AWS Deadline Cloud — open ideas

- [x] CreateQueue/UpdateQueue + PassRole -> AssumeQueueRoleForUser full-role vend (privesc) — DONE,
  VERIFIED live. See tested.md.
- [ ] **Fleet-role privesc parallel** — CreateFleet/UpdateFleet `--role-arn` + AssumeFleetRoleForWorker?
  ForRead is read-narrowed; is ForWorker narrowed? Needs a worker registration to test (heavier).
- [ ] **CreateMonitor `--role-arn` + identityCenterApplicationArn** — Monitor wires an Identity Center
  app; check whether the monitor role or the IC app is abusable (needs IC, not in member acct).
- [ ] **jobRunAsUser / job attachments** — a submitted job runs on workers as the queue role; if you can
  submit jobs to a privileged queue (CreateJob), the job payload executes with queue-role creds on the
  worker (RCE-as-role). Needs a fleet+worker (compute cost) to test end-to-end.
