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
- [ ] Reconcile the post-exploitation page's older authenticated-pull observation with the current
      official audit contract, which documents Docker/package download methods as Data Access when
      Data Read logging is enabled.
- [ ] Recheck the gcr.io persistence technique's complete permission chain: namespace reservation can
      use `repositories.create`, but attacker content additionally needs `uploadArtifacts`; confirm
      the one-shot Create-on-Push Writer path against current migration/redirection state.
- [ ] Review whether current Artifact Registry platform logs provide a useful additional signal for
      artifact pulls and remote/virtual resolution without overstating Cloud Audit Log coverage.
