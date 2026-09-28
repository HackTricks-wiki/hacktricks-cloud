# Storage Transfer Service — open validation leads

- [ ] With disposable buckets and a minimum custom role, confirm whether a create-only principal can
  force prompt execution solely through a one-time schedule without `storagetransfer.jobs.run`.
- [ ] Revalidate which changes to a user-managed-SA job trigger an `iam.serviceAccounts.actAs` check:
  destination-only patch, status enablement, source change, and logging-only patch.
- [ ] Re-test `jobs.run` on an already-enabled user-managed-SA job after removing the runner's
  `iam.serviceAccounts.actAs`. Current documentation describes accounts that create or trigger a job
  as restricted to approved service accounts, so the old no-`actAs` result must not be republished
  until confirmed against the current service.
- [ ] Capture the current caller/managed-agent/user-managed-SA principals on Cloud Storage Data
  Access entries and optional TransferActivityLog records for the same harmless marker object.
- [ ] Test IAM Conditions on `storagetransfer.jobs.update`/`.run` against job resource names and
  document whether conditions can prevent cross-job replay or destination replacement.

All live validation must use a random non-secret marker, must not enable destructive transfer
options, and must delete jobs, buckets, objects, and IAM grants immediately after capture.
