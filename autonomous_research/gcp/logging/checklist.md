# Cloud Logging — open leads

Last researched: 2026-09-28

## Regression checks

- [ ] Re-check the Cloud Logging audit-method table after major API releases. In particular, watch
      whether `WriteLogEntries` or `TailLogEntries` becomes audited and whether `CopyLogEntries`
      remains `DATA_READ`.
- [ ] Re-check `roles/viewer` for `logging.buckets.copyLogEntries`; the permission currently turns a
      basic read-only project role into a bulk historical export capability.
- [ ] Re-check linked BigQuery dataset query requirements and access inheritance. Current official
      guidance requires BigQuery Data Viewer, `logging.links.list`, and a query-job permission; don't
      restore claims about automatic `projectReaders` access without current official or live proof.
- [ ] Re-check default Logging settings semantics. `disableDefaultSink`, storage location, CMEK, and
      `defaultSinkConfig` currently affect newly created resources only, not existing descendants.
- [ ] Re-check `bucket_changed_parent_project` handling before reconsidering sink destination
      bucket-name reuse. Do not restore the historical hijack technique unless current behavior is
      independently reproducible.

## Future minimum-permission tests

- [ ] Confirm whether the current `gcloud logging copy` client performs any discovery calls beyond
      the API's documented `logging.buckets.copyLogEntries`; distinguish CLI convenience permissions
      from the server-side minimum.
- [ ] Confirm which exact BigQuery permissions a direct `bq query` against a linked dataset exercises
      in addition to `bigquery.jobs.create`, and record the resulting BigQuery audit fields.
- [ ] Confirm view-level `SetIamPolicy` `resourceName` and request-policy fields in a disposable custom
      view; the current book entry uses the official method name and class without claiming unverified
      field placement.

## Constraints

- Do not create or delete production log buckets, links, sinks, views, metrics, exclusions, or IAM
  bindings for these checks.
- Bucket lock and CMEK attachment are irreversible or operationally risky. Test only on disposable
  buckets and clean every reversible resource immediately.
- A log bucket deletion has a seven-day recovery window and continues receiving routed entries while
  `DELETE_REQUESTED`; restore it during the same test session. Delete active links first. A locked
  bucket isn't a valid deletion test target until every stored entry has fulfilled its retention
  period.
