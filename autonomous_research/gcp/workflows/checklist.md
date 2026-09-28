# Workflows — open research

## 2026-09-28 verified documentation contracts

- [x] Workflow creation with an explicit service account: create, `actAs`, execution-create boundary
  and LRO polling distinction.
- [x] Omitted `serviceAccount` selects the default Compute Engine service account but still requires
  `iam.serviceAccounts.actAs` on that effective identity, with impact bounded by its existence and grants.
- [x] Execute-only boundary does not re-check `actAs` and is limited to the deployed definition and
  its attacker-controlled inputs.
- [x] Source-only workflow PATCH retains the stored identity; changing the identity remains an
  attachment operation.
- [x] Callback send/list REST surface, exact permissions, lack of gcloud callback commands, and
  off-by-default Data Access audit methods.
- [x] Current workflow-definition and execution audit classes, service names, v1 method names,
  operation-polling telemetry, automatic start/end platform logs, call-log precedence, and
  permission-gated per-call logging.
- [x] Removed/folded post-exploitation reads, connector examples, token mechanics, egress notes and
  duplicate CLI headings from the privilege-escalation page.

## Open bounded validation

- [ ] Revalidate with a disposable custom role that omitting `serviceAccount` on a v1 create is denied
  without `iam.serviceAccounts.actAs` on the default Compute Engine service account, and capture the
  exact failed-authorization resource without retaining a workflow.
- [ ] Capture current v1 `CreateWorkflow`/`UpdateWorkflow` LRO start and completion entries and record
  whether `sourceContents`, update masks and retained `serviceAccount` are consistently present or
  subject to truncation/redaction.
- [ ] Capture `CreateExecution`, `SendHttpCallback`, `ListCallbacks`, automatic `executions_system`
  records and optional `engine_call` records in one disposable fixture with Data Access toggled only
  for the test window.
- [ ] Test callback discovery end-to-end with only `executions.list`, `callbacks.list` and
  `callbacks.send`, including derivation of the send endpoint from the returned Callback resource
  name and accepted HTTP method.
