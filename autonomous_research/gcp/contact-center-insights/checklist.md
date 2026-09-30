# Contact Center Insights — research checklist

## Completed in the 2026-09-28 documentation pass

- [x] Reconcile transcript/analysis reads with `FULL`, `BASIC` and structured-transcript views.
- [x] Verify current Viewer role includes project-wide signed-audio generation.
- [x] Correct signed-audio HTTP verb, response shape and Storage-side telemetry.
- [x] Bound the GCS service-agent deputy to supported conversation formats.
- [x] Verify create versus upload/ingest redaction and long-running-operation behavior.
- [x] Verify cross-project export caller permission, service-agent boundary, table/location prerequisites and default write disposition.
- [x] Replace inferred audit classes/methods with the current official audit catalog.
- [x] Remove destructive-only, persistence and low-value enrichment headings from post-exploitation.

## Safe future validation

- [ ] In a disposable no-production-data project, create one minimal supported transcript object and grant only `storage.objects.get` to the Insights service agent. Confirm that a caller with only `conversations.create` plus `conversations.get` can import/read it, then delete the conversation, object, bucket and temporary IAM bindings.
- [ ] Repeat with malformed JSON and a non-conversation binary to document exact parser rejection and prove the arbitrary-object bound.
- [ ] With Customer Experience Insights and Cloud Storage Data Access enabled temporarily, capture exact `CreateConversation`, service-agent `storage.objects.get`, `GetConversation`, `GenerateConversationSignedAudio` and signed-URL fetch entries; restore the original audit policy afterward.
- [ ] In attacker-owned disposable BigQuery resources, grant the source Insights service agent only the narrow documented dataset access needed for export. Confirm whether its existing source-project `bigquery.jobs.create` suffices cross-project, record exact `JobInsertion`/`JobChange`/`TableDataChange` actors and fields, then remove the table, dataset and grant.
- [ ] Verify whether `ExportInsightsData` succeeds for a custom caller role containing only `contactcenterinsights.conversations.list`, documenting the current discrepancy with the unused-looking `.conversations.export` permission.
- [ ] Measure signed-audio URL lifetime and exact multi-leg/turn-level response variants without retaining any real customer audio.

## Open hypotheses / rejected for now

- [ ] Test whether a direct `CreateConversation` transcript import bypasses project redaction settings exactly as its “does not support redaction” contract implies. Treat as expected behavior, not a vulnerability, unless a documented security boundary is crossed.
- [ ] Explore whether metadata URIs or multi-leg audio sources expand the same service-agent deputy beyond already documented supported formats. Do not add a separate technique without distinct impact.
- [ ] Revisit authorized-view and dataset export/signed-audio endpoints for scope leaks. Current documentation indicates separate permissions and no cross-scope bypass.
- [ ] Rejected: deletion as post-exploitation. It is destructive denial of service and not a disclosure primitive.
- [ ] Rejected: `settings.update` as post-exploitation. It is configuration persistence and is bounded to documented ingestion paths.
- [ ] Rejected: creating a new analysis as a standalone technique. It enriches data the caller can already read and does not create a new authorization crossing.
