# Sensitive Data Protection (DLP) — tested and documentation-audited

## Previously verified live observations

- A Cloud Storage inspection job with `includeQuote: true` wrote raw detected strings to the chosen
  BigQuery findings table through the DLP service agent.
- Inline `content:inspect` returned quoted values supplied in the request, but it did not retrieve
  any victim-side data and therefore is not retained as a standalone attack technique.
- A de-identify template containing `cryptoKey.unwrapped.key` returned the base64 raw key to a caller
  with `dlp.deidentifyTemplates.get`; a compatible deterministic-encryption token was subsequently
  re-identified with that key.
- Updating a de-identify template so that it no longer targeted `EMAIL_ADDRESS` caused later uses of
  the template to pass the email through unmasked.
- Raising an inspect template's `minLikelihood` to `VERY_LIKELY` suppressed a finding that the prior
  configuration returned.

These historical observations were not repeated during the 2026-09-28 audit. No cloud resources or
IAM policies were read or changed in this documentation pass.

## 2026-09-28 — post-exploitation and persistence audit

The post-exploitation page retains five bounded techniques:

1. Create a storage inspection job that reads through the already-authorized DLP service agent and
   exports quoted findings.
2. Read jobs, templates, triggers, and existing Discovery profiles as a sensitivity map.
3. Read a de-identify template that embeds an unwrapped AES key and use the key to reverse compatible
   deterministic/FPE tokens obtained elsewhere.
4. Update a shared de-identification template so selected values pass through unmasked on later use.
5. Update a shared inspection template to suppress findings on later use.

The recurring job-trigger technique moved to a dedicated persistence page because it continues
running after the creator loses access. It is explicitly classified as service-level data-collection
persistence, not identity or IAM persistence.

Material corrections and bounds:

- Replaced the blanket “DLP calls are unlogged by default” claim with the current official audit
  contract. `CreateDlpJob`, `CreateJobTrigger`, `UpdateDeidentifyTemplate`, and
  `UpdateInspectTemplate` are Admin Activity and always logged. DLP reads such as list/get and
  `ReidentifyContent` are Data Access and normally off by default.
- Recorded that BigQuery Data Access logging cannot be disabled, while avoiding a guarantee that
  every DLP findings write emits a table-data event: BigQuery documents gaps for `InsertAll`,
  Storage Write API appends, and failed jobs.
- Bounded the job primitive to the DLP service agent's effective access. It does not bypass IAM,
  VPC-SC, CMEK, or cross-project authorization. Cross-project findings export requires the service
  agent to have write access in that destination; an attacker can grant it in an attacker-owned
  project.
- Added `serviceusage.services.use` for billable job/content calls and the conditional
  `dlp.inspectTemplates.get` requirement when a job references a template.
- Corrected predefined-role drift. Current basic `roles/viewer` includes DLP job/template/trigger
  reads and all four data-profile families, including file-store profiles. `roles/dlp.reader` does
  not include data-profile permissions.
- Narrowed raw-key exposure to templates that actually use `cryptoKey.unwrapped.key`. KMS-wrapped
  keys remain ciphertext, transient keys are discarded, and HMAC hashing is not reversible.
- Bounded re-identification to tokens the attacker separately obtains and to the matching transform,
  surrogate, and context configuration.
- Removed the standalone `content:inspect` heading because classifying caller-supplied content does
  not disclose victim data or cross a privilege boundary.
- Corrected job-trigger minimum permissions: current audit/IAM contracts require both
  `dlp.jobTriggers.create` and `dlp.jobs.create`; `roles/dlp.jobTriggersEditor` lacks the latter and
  is insufficient alone.
- Added cost and cleanup warnings for jobs/triggers and stopped claiming DLP job records are
  cost-free or require no cleanup.

## No zero-day conclusion

All retained behaviors match documented service-agent delegation, template semantics, REST fields,
IAM permissions, and audit categories. This audit found documentation errors and dangerous expected
functionality, but no unexpected GCP vulnerability requiring a private bug-bounty report.

## 2026-09-28 — independent cross-review

An independent official-documentation and read-only IAM-role review found and corrected these
remaining issues:

- Replaced the nonexistent generic `dlp.*DataProfiles.*` shorthand with the exact profile
  permissions. File-store profiles use `dlp.fileStoreProfiles.get/list`, while the other three
  families use `dlp.{project,table,column}DataProfiles.get/list`.
- Corrected profile enumeration so it uses each profile's data region and the scope that created it.
  Project Discovery profiles are read under `projects/...`; organization/folder Discovery profiles
  are read under `organizations/...`. The `global` location is not a cross-region aggregator.
- Split `ListDlpJobs` (`DATA_READ`) from the template/trigger/profile list methods (`ADMIN_READ`).
  All are Data Access and off by default for DLP. The current service catalog explicitly marks
  `CreateDlpJob` Admin Activity; this must not be re-derived from its mixed permission list.
- Qualified downstream BigQuery telemetry. BigQuery Data Access logging is non-disableable, but the
  DLP `saveFindings` documentation does not promise its internal write method, and BigQuery omits
  `TableDataChange` for `InsertAll` and Storage Write API appends. The page therefore lists the
  possible table/job signals without claiming a guaranteed destination-write event.
- Added the documented cross-project service-agent bounds used by the examples: Storage Object
  Viewer on a source bucket and BigQuery Data Editor on a destination dataset (or existing table).
  Dataset scope is needed when the output table must be created.
- Extended the reversible-template technique without conflating key disclosure and key use. An
  unwrapped template exposes reusable AES key material. A KMS-wrapped template does not expose the
  plaintext key, but server-side re-identification is possible with template read,
  `serviceusage.services.use`, `dlp.kms.encrypt`, and a DLP service agent that has
  `cloudkms.cryptoKeyVersions.useToDecrypt` on a location-compatible key. KMS `Decrypt` is a
  separate, off-by-default Data Access event whose principal is the DLP service agent.
- Rechecked the current GA predefined roles read-only with `gcloud iam roles describe`:
  `roles/viewer` still contains all four profile families and the relevant DLP reads;
  `roles/dlp.reader` still omits profile permissions; and `roles/dlp.jobTriggersEditor` still omits
  `dlp.jobs.create`.
- Confirmed the REST request envelopes: `dlpJobs.create` accepts top-level `inspectJob`, and
  `jobTriggers.create` accepts top-level `jobTrigger` plus `triggerId`. The SUMMARY entries resolve
  to both pages.

No cloud resources, APIs, IAM policies, jobs, triggers, templates, or data were changed during this
cross-review.
