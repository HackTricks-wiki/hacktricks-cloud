# Artifact Registry — open validation

- [ ] In a disposable repository, retest Docker push and pull with Artifact Registry `DATA_WRITE` and
      `DATA_READ` explicitly enabled at every effective hierarchy level. Capture
      `Docker-StartUpload`, `Docker-FinishUpload`, `Docker-PutManifest`, `Docker-GetManifest`, and
      `Docker-ServeBlob`; restore the audit policy and delete all test artifacts.
- [ ] Revalidate direct REST `tags.patch` with only `artifactregistry.tags.update`, including a nested
      Docker package name that must be URL-escaped, immutable-tag rejection, and exact `UpdateTag`
      request/response fields. Restore the original tag and remove test versions.
- [ ] Revalidate a blind repository `setIamPolicy` request with only
      `artifactregistry.repositories.setIamPolicy`, then separately test the CLI's
      `getIamPolicy` requirement and an intentional stale-`etag` conflict. Restore the original
      policy byte-for-byte.
- [x] Correct `ExportArtifact` telemetry in the Artifact Registry post-exploitation page: it is an
      off-by-default Data Access `DATA_READ` LRO rather than Admin Activity.
- [x] Reconcile the post-exploitation page's older authenticated-pull observation with the current
      official audit contract, which documents Docker/package download methods as Data Access when
      Data Read logging is enabled.
- [ ] Recheck the gcr.io persistence technique's complete permission chain: namespace reservation can
      use `repositories.create`, but attacker content additionally needs `uploadArtifacts`; confirm
      the one-shot Create-on-Push Writer path against current migration/redirection state.
- [x] Review whether current Artifact Registry platform logs provide a useful additional signal for
      artifact pulls and remote/virtual resolution without overstating Cloud Audit Log coverage.
- [ ] Validate `ExportArtifact` against a disposable source and destination to identify the runtime
      writer identity, exact cross-project bucket prerequisites, destination object names, overwrite
      behavior, VPC-SC behavior, and the source/destination audit principals. Remove the exported
      objects and source repository after the test.
- [ ] Test `gcloud artifacts attachments create` under a custom role containing only
      `artifactregistry.attachments.create` and `artifactregistry.files.upload`, then test direct
      creation from pre-existing file resources to determine whether only `attachments.create` is
      sufficient. Remove all files and attachments afterward.
- [ ] Verify project/location versus explicit repository platform-log precedence in a disposable
      repository, including which request records the disabling operation itself. Restore both
      configurations exactly and delete the repository afterward.
- [x] Reconcile current platform-log inheritance/default wording across the product guide and gcloud
      help; document the discrepancy and use explicit disable rather than clear as the deterministic
      action.
- [x] Bound the public-resource exception to Data Access reads without obscuring the always-on
      `SetIamPolicy` Admin Activity event or separately configured platform logs.
- [x] Mark destination-side Cloud Storage telemetry for `ExportArtifact` as conditional because the
      current REST contract does not publish the backend writer or guarantee a Storage audit event.
- [x] Separate direct attachment-create permission from the local-file upload wrapper and record the
      complete Version/Package/Repository REST target scope.
