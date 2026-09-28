# Vertex Ai — open ideas

Open ideas — Vertex AI.

AI/ML fan-out + permission sweep both closed (0 gaps). No open candidate. Revisit on new
`aiplatform.*` subservices (e.g. new agent / RAG / tuning surfaces).

## Follow-ups from 2026-09 privilege-escalation audit

- [ ] Verify `CreateReasoningEngine` and `CreateNotebookExecutionJob` audit class/default visibility
  in a no-cost authorized project when those resources can be created and immediately cleaned up;
  the current official Vertex AI audit-method catalog omits both.
- [ ] Re-check whether Google publishes a dedicated current Workbench audit-method matrix. Until it
  does, retain write-operation/Admin Activity semantics but avoid inventing DATA_READ/DATA_WRITE
  coverage for notebook proxy or guest activity.
- [ ] Move the already verified RAG confused-deputy technique to the Vertex AI post-exploitation
  page on the next scoped pass; do not re-add it as privilege escalation.
- [ ] Revisit managed `tuningJobs` only if a future API exposes caller-controlled code, container,
  command, plugin, or deserialization input in the tuning runtime. Merely attaching a service
  account to a managed tuning workflow is not enough to claim arbitrary-SA code execution.
- [ ] Verify the raw `CreateBatchPredictionJob` custom-service-account delegation failure mode in an
  authorized no-cost test: distinguish caller `iam.serviceAccounts.actAs` rejection from a missing
  Vertex AI Service Agent per-account prediction grant, and record the exact principal/error.
