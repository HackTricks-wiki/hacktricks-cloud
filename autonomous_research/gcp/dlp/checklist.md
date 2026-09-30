# Sensitive Data Protection (DLP) — open validation

- [ ] With a disposable bucket and dataset, retest `dlp.jobs.create` under a custom role containing
      only `dlp.jobs.create` plus `serviceusage.services.use`; separately reference a template to
      confirm the additional `dlp.inspectTemplates.get` check. Delete the job, output, and source.
- [ ] Capture current `CreateDlpJob` Admin Activity in a clean project and determine which request
      fields are retained or redacted, without relying only on the audit-method catalog.
- [ ] Repeat a tiny Cloud Storage-to-BigQuery findings export with Storage Data Read explicitly
      enabled. Record the DLP, source Storage, and destination BigQuery principals/methods, then
      restore the audit policy exactly and delete all assets.
- [ ] Validate cross-project `saveFindings` with the minimum destination grant on a single test table
      or dataset; then remove the grant and delete the output.
- [ ] Recheck the exact response projection for `cryptoKey.unwrapped.key` on both project- and
      organization-scoped templates, then delete the disposable templates and keys.
- [ ] Test `content:reidentify` with a recovered unwrapped key under only
      `serviceusage.services.use`, and separately live-verify the documented KMS-wrapped path:
      template read plus `dlp.kms.encrypt` for the caller and
      `cloudkms.cryptoKeyVersions.useToDecrypt` for the request project's DLP service agent. Capture
      whether the KMS `Decrypt` entry identifies that service agent, then delete all test data.
- [ ] Create a one-day disposable job trigger under a two-permission custom role
      (`dlp.jobTriggers.create`, `dlp.jobs.create`) plus `serviceusage.services.use`; confirm that
      `roles/dlp.jobTriggersEditor` alone fails, capture its Admin Activity record, and delete the
      trigger before it fires.
- [ ] Determine whether scheduled trigger executions create a distinct DLP audit record or only
      data-plane source/destination entries. Do not state a runtime `CreateDlpJob` event without this
      evidence.
- [ ] Enumerate regional Discovery profiles in a project with profiling enabled and record exactly
      which fields basic `roles/viewer` can see for project, table, column, and file-store profiles;
      separately verify the project parent versus organization parent visibility boundary.
- [ ] Review DLP connections, stored infoTypes, estimates, subscriptions, and content policies for
      additional high-value secrets, delegated identities, mutable detection controls, or
      cross-project actions before adding any new book technique.
