# Workflows — tested and documented

## 2026-09-28 — privilege-escalation page audit

- Reduced the page to four genuine escalation boundaries: attacker-authored workflow creation,
  invocation of an existing privileged workflow, source-only takeover of an existing attached
  identity, and callback injection into a paused privileged execution.
- Consolidated Secret Manager connector access, OAuth/OIDC calls, external HTTP egress and CLI
  deployment into the create/update run-as primitives. They are execution mechanisms or examples,
  not independent escalation permissions.
- Removed workflow-source, execution-result and detailed-history reads from this page. Those are
  post-exploitation disclosure paths and belong in the Workflows post-exploitation material.
- Bounded `workflows.executions.create`: it starts the latest fixed workflow revision and does not
  grant arbitrary use of the attached service account. Escalation requires a useful privileged side
  effect or attacker-controlled input that the workflow consumes.
- Preserved the source-only update boundary. A PATCH with `updateMask=sourceContents` retains the
  existing service account; attaching a different service account is a separate change requiring
  `iam.serviceAccounts.actAs`.
- Preserved the default Compute Engine service-account creation variant. Official documentation says
  omission of `serviceAccount` assigns that identity; the deployer still needs
  `iam.serviceAccounts.actAs` on the effective default account. Its impact is conditional on the
  account existing and retaining useful roles. New organizations normally suppress automatic Editor
  grants.
- Corrected minimum API permissions: workflow create/update are independent LRO writes;
  `workflows.operations.get` is only for polling. A bare execution create requires only
  `workflows.executions.create`; waiting for or retrieving its result needs read access.
- Corrected audit contracts to current v1 methods. Workflow create/update are always-on Admin
  Activity LROs under `workflows.googleapis.com`. Execution create and callback send/list are Data
  Access under `workflowexecutions.googleapis.com` and are off by default. Workflows still emits
  automatic execution start/end platform logs; per-call logs are conditional on call logging.
- Local CLI help confirmed regional arguments, deploy `--async`, execute-versus-run behavior,
  per-execution `--call-log-level=log-none`, and the absence of a callbacks gcloud subgroup.

This pass used official documentation and local CLI/source inspection only. It did not call GCP APIs,
enable services, create workflows, start executions, or change cloud state.

## Prior live claims retained but not repeated in this pass

- The prior page recorded successful validation that OAuth-authenticated workflow requests run as
  the attached service account, and that source-only updates retain an already attached identity
  without a new `actAs` check.
- It also recorded that an omitted service-account field selected the default Compute Engine service
  account, and that execution creation/callback activity was absent without Data Access logging while
  automatic execution state logs remained. The old inference that omission avoided `actAs` was not
  retained because current official attachment requirements and troubleshooting guidance require it.
  Emitted payload fields should still be periodically revalidated in a disposable project.

## 2026-09-28 — independent cross-review

- Corrected the omitted/default-service-account path: omission selects the default Compute Engine
  service account but is not a documented `iam.serviceAccounts.actAs` bypass.
- Distinguished raw API minimums from current CLI behavior: `gcloud workflows deploy` performs an
  initial `GetWorkflow`; `--async` skips operation polling only. `execute` returns after creation,
  whereas `run` polls with execution-read access.
- Added the off-by-default `google.longrunning.Operations.GetOperation` audit signal for create and
  update polling, while retaining the exact v1 create/update/execution/callback methods and service
  names.
- Bounded `engine_call` visibility to explicit call steps when call logging is enabled and the
  workflow identity has `logging.logEntries.create`; connector/expression/internal-library calls are
  excluded, authorization headers are redacted, and execution-level settings take precedence.
- Reconfirmed that callbacks need a live endpoint and accepted method, and that Workflows permissions
  are granted at project scope rather than through a per-workflow allow policy. No cloud APIs or
  resources were touched.
