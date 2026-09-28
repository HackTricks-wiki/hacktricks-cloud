# Vertex Ai — open ideas

Open ideas — Vertex AI.

The broad AI/ML fan-out and permission sweep are complete, but the targeted validation items below
remain open. Revisit on new `aiplatform.*` subservices and on changes to agent, RAG, Feature Store,
and tuning surfaces.

## Follow-ups from 2026-09 privilege-escalation audit

- [ ] Verify `CreateReasoningEngine` and `CreateNotebookExecutionJob` audit class/default visibility
  in a no-cost authorized project when those resources can be created and immediately cleaned up;
  the current official Vertex AI audit-method catalog omits both.
- [ ] Re-check whether Google publishes a dedicated current Workbench audit-method matrix. Until it
  does, retain write-operation/Admin Activity semantics but avoid inventing DATA_READ/DATA_WRITE
  coverage for notebook proxy or guest activity.
- [x] Move the already verified RAG confused-deputy technique to the Vertex AI post-exploitation
  page; do not re-add it as privilege escalation.
- [ ] Revisit managed `tuningJobs` only if a future API exposes caller-controlled code, container,
  command, plugin, or deserialization input in the tuning runtime. Merely attaching a service
  account to a managed tuning workflow is not enough to claim arbitrary-SA code execution.
- [ ] Verify the raw `CreateBatchPredictionJob` custom-service-account delegation failure mode in an
  authorized no-cost test: distinguish caller `iam.serviceAccounts.actAs` rejection from a missing
  Vertex AI Service Agent per-account prediction grant, and record the exact principal/error.

## Follow-ups from 2026-09-28 end-to-end audit

- [x] Move the verified RAG import/retrieve deputy out of privilege-escalation classification and
      into the post-exploitation page with current RAG Data Service Agent bounds.
- [x] Replace historical third-party Agent Engine tenant/producer claims with current official
      custom/default runtime identity coverage.
- [x] Verify current GA Viewer/User/RAG/Custom-Code Service Agent role contents and record the
      no-`actAs` Custom Code Service Agent token-mint boundary.
- [x] Correct Model versus Endpoint container-spec ownership and the CustomJob service-account field.
- [x] Bound model export to `supportedExportFormats` and dataset export to metadata/annotations.
- [x] Assess persistence/unauthenticated coverage: reject duplicate schedule/deployment/startup-script
      headings and do not invent anonymous access for publicly reachable prediction networking.
- [ ] In a disposable project, call Feature View `FetchFeatureValues` and
      `SearchNearestEntities` with Vertex AI Data Access logging both disabled and enabled. Capture
      exact `protoPayload.methodName`, service name and permission because the current audit catalog
      omits these methods; delete every online-store/view test resource afterward.
- [ ] Recheck stable-v1 versus v1beta1 RAG method names in enabled Data Access logs. Existing lab
      evidence proves default silence and data returned, but the current public audit catalog still
      omits `RetrieveContexts`.
- [ ] Test `models.export` and `datasets.export` with only their raw permission and a controlled
      bucket grant to distinguish RPC minimum from operation-polling/model-get helper permissions;
      use synthetic artifacts and delete all exports and grants immediately.
