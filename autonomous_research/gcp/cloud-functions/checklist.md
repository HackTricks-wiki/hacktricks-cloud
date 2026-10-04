# Cloud Run functions — open research

## 2026-09-28 verified documentation contracts

- [x] Separate function runtime and Cloud Build service accounts.
- [x] Current `gcloud functions deploy` runtime/build account flags and default-account wording.
- [x] `cloudfunctions.functions.create`, `.update`, `.get`, invocation, and generation-specific
      source-upload permission boundaries in current documentation.
- [x] Node.js buildpack `build` and `gcp-build` execution during source deployment.
- [x] Cloud Build metadata-server credential access for a user-specified build identity.
- [x] Cloud Functions create/update/upload/read audit classes and LRO behavior.
- [x] Upload telemetry reconciliation: v1 and v2 `GenerateUploadUrl` are `ADMIN_WRITE` and observed/
      classified as Admin Activity; the generated v1 method-detail's conflicting Data Access label
      is recorded as documentation inconsistency rather than treated as runtime truth.
- [x] IAM documents a separate Admin Activity record with method `iam.serviceAccounts.actAs` when a
      service-account attachment check is evaluated.
- [x] Preservation-safe environment-only PATCH merges the current map and therefore adds
      `cloudfunctions.functions.get` to the raw `.update` boundary.
- [x] Removed non-escalation invocation/public-exposure material, an unsupported source-bucket race,
      and the digest-pinned Artifact Registry negative result from the privilege-escalation page.
- [x] Rebuild post-exploitation around signed source download and direct managed-bucket reads;
      remove deletion, duplicate source replacement and generic in-process code injection.
- [x] Correct `GenerateDownloadUrl` to the current documented `ADMIN_READ` Data Access event and
      refresh predefined-role inclusion for `sourceCodeGet`.

## Safe live validation frontier

- [ ] With disposable user-managed runtime and build accounts, subtract permissions from a raw v2
      source deployment to distinguish direct API minimums from `gcloud` helper reads/polling. Use a
      synthetic low-privilege target identity and delete the function, source objects, image, build
      logs/captures, accounts, roles, and bindings immediately.
- [ ] Capture successful and denied `actAs` attachment records for
      runtime-only, explicitly selected build-account, Compute-default-builder, and legacy-builder
      configurations. Do not assume every project has the same default build identity.
- [ ] Validate one harmless Node.js `gcp-build` metadata proof with a user-managed build account and
      record token scope/lifetime and downstream principal attribution. Never print or retain the
      bearer token; exfiltrate only a non-secret identity claim and delete the receiver capture.
- [ ] Revalidate a direct v2 environment-only PATCH against a function whose image contains a benign
      startup hook. Confirm whether Cloud Build reruns, which attached accounts are revalidated, and
      the exact request/update-mask fields logged.
- [ ] Determine whether any managed source-upload generation can be replaced by a Storage-only
      principal before consumption. Keep this out of the book unless a reliable generation/path
      discovery and integrity failure is demonstrated; keep a real platform boundary failure private.
- [ ] With Data Access enabled only on a disposable project, capture current v1 and v2
      `GenerateDownloadUrl` entries and the subsequent signed object GET. Verify the Storage
      principal/resource fields without placing a secret in source, then restore the exact audit
      policy and remove the function, source archive, build outputs and every temporary binding.

## Cleanup contract for every fixture

- [ ] Delete all test functions and Eventarc/Pub/Sub/Scheduler triggers.
- [ ] Delete managed test source objects and Artifact Registry packages when the service does not
      remove them automatically; verify no test revision remains in Cloud Run inventory.
- [ ] Delete every build, log/capture containing credential material, service account, custom role,
      IAM binding, test bucket, topic, subscription, receiver, and key.
- [ ] Restore Cloud Functions, Cloud Build, Artifact Registry, Eventarc, Pub/Sub, Run, Logging, and
      Storage APIs and audit configurations to their original state, then verify Cloud Asset/IAM and
      service inventories contain no fixture identifier.
