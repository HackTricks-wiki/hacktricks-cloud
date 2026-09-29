# Vertex Ai — tested

Vertex AI. 12 retained privilege-escalation techniques and 5 retained post-exploitation families:
workload-spec disclosure, model/image-dataset export, RAG read-back, Feature View data reads, and
Semantic Governance defense evasion.

## 2026-09-29 Semantic Governance policy boundary

- Added policy update/delete as a bounded defense-evasion path: a Vertex AI User can replace the
  natural-language constraint, move its agent/tool scope, or delete it, removing only the semantic
  intent/business-rule guardrail. The agent still needs all original tool and downstream authority.
- Safe nonexistent-resource probes captured exact always-on Admin Activity for
  `UpdateSemanticGovernancePolicy` and `DeleteSemanticGovernancePolicy`; the latter was independently
  denied to a no-role caller on `aiplatform.semanticGovernancePolicies.delete`.
- Engine `.update` does not authorize the documented deprovision RPC. The backend checks an
  unpublished `.deprovision` permission absent from testable-permission results and all checked
  predefined roles, so deprovision is recorded as a product-contract discrepancy rather than an
  attack technique.
- No engine/policy was provisioned. All disposable identities, roles, bindings, keys and isolated
  configs were removed, and the pre-existing engine remained `INACTIVE`. Full evidence and the
  private-first follow-up matrix are in `semantic-governance/`.

## VERIFIED LIVE — RAG Engine confused-deputy
- CreateRagCorpus (LRO) → `ragFiles:import` (importedRagFilesCount=1) → `:retrieveContexts` returned
  the object plaintext verbatim. `ragCorpora.query` read-back is in `roles/aiplatform.viewer` (low
  priv). Audit: CreateRagCorpus/DeleteRagCorpus = ADMIN_WRITE (always on); ImportRagFiles +
  RetrieveContexts produced no activity entry under that test's default audit configuration. The
  import is cataloged as Data Write; `RetrieveContexts` is absent from the current audit catalog, so
  no audit class is inferred from the no-log observation.
- The historical capture recorded `DeleteRagCorpus` and teardown, but did not preserve the exact
  post-delete get/list response or whether any bucket object/IAM grant had existed. Treat that as an
  evidence-quality gap rather than inventing a stronger cleanup claim; future runs must retain the
  completed delete LRO plus absent get/list and bucket/IAM inventories.

## Excluded
- Dialogflow `agents.export` / conversation-transcript exfil — borderline, below bar.

## 2026-09 documentation audit — privilege-escalation page

- Kept the independently useful run-as identities: custom training with a selected SA, custom
  training with the default Custom Code Service Agent, endpoint and batch custom prediction,
  pipelines, hyperparameter trials, Agent Engine, Colab execution jobs, and current Workbench
  instance create/update/IAM paths.
- Corrected audit claims against the current Vertex AI audit-method catalog. The catalog explicitly
  classifies `CreateCustomJob`, `CreateBatchPredictionJob`, `CreatePipelineJob`,
  `CreateHyperparameterTuningJob`, `UploadModel`, `CreateEndpoint`, and `DeployModel` as always-on
  Admin Activity. It does not currently enumerate `CreateReasoningEngine` or
  `CreateNotebookExecutionJob`; their exact class/default visibility is now marked undocumented
  instead of asserted as Admin Activity.
- Corrected default-training semantics: CustomJob, HyperparameterTuningJob, and custom
  TrainingPipeline containers default to the Custom Code Service Agent, so this is a no-`actAs`
  code-execution path. The current managed role includes service-account token/signing permissions;
  with its normal project-level grant the agent can mint a token for another service account in
  that project. This is bounded by the actual binding, deny/PAB controls, and any cross-project
  target policy; it must not be described as unconditional Owner.
- Folded `trainingPipelines.create` into the CustomJob primitive and recurring Colab schedules into
  the notebook-execution primitive. Removed DeploymentResourcePool/PersistentResource as standalone
  escalation headings because each still requires a separate executable model/job path.
- Removed from privesc: exports/imports, Feature Store/View/Vector Search, metadata-store and RAG
  reads/poisoning, and managed foundation-model tuning. Those are post-exploitation/integrity paths,
  not independent caller-controlled run-as primitives.
- Documentation-only review; no project resources were created or modified.

## 2026-09 independent-review corrections

- Removed the false claim that an instance IAM self-grant of `notebooks.instances.use` opens
  JupyterLab. Workbench's single-user/service-account access mode is selected at creation and cannot
  be changed later through instance IAM. Retained the useful policy path only as a self-grant of
  `notebooks.instances.update` plus `notebooks.instances.reset`, followed by startup-script injection;
  the documented CLI IAM helper also needs `notebooks.instances.getIamPolicy`.
- Corrected Workbench creation prerequisites: a custom instance service account must be in the same
  project, the creator needs `iam.serviceAccounts.actAs`, and interactive access depends on the
  immutable access mode (including `actAs` for service-account mode), not merely
  `notebooks.instances.use`.
- Added the distinct no-`actAs` Agent Engine default: an omitted runtime service account executes as
  the Reasoning Engine Service Agent. Impact is bounded to its managed role and current bindings.
- Separated the permissions documented on raw endpoint/batch create RPCs from extra read permissions
  used by `gcloud`/SDK helpers, and recorded the Vertex AI Service Agent's per-custom-account
  prediction delegation prerequisite. Also corrected Colab CLI support for `--direct-content`.
- Replaced short audit action labels with fully qualified RPC method names, including
  `google.iam.v1.IAMPolicy.SetIamPolicy`; classifications and catalog omissions remain explicit.

## 2026-09-28 end-to-end expected-attack audit

No Vertex AI resource or project state was accessed or changed. Current official REST/RPC and audit
catalogs, local discovery schemas, current GA predefined-role definitions, and local CLI help were
used.

### Retained post-exploitation techniques

- **Workload-spec disclosure.** Kept one consolidated read primitive for pipeline, custom/tuning,
  batch, model, and endpoint resources. Corrected the old claim that every resource list and every
  endpoint embeds container environment variables: get is the reliable complete-resource path,
  `PipelineJob.list` is the separately verified exception, and model container config must be read
  from the referenced Model rather than Endpoint.
- **Server-side model/dataset export.** `models.export` and `datasets.export` are in
  `roles/aiplatform.user`; the Vertex AI P4SA writes to a caller-selected bucket. Impact is bounded:
  only advertised/exportable model formats work, dataset export supports image rather than tabular
  datasets, and it returns metadata/annotations rather than arbitrary source objects.
- **RAG read-and-retrieve deputy.** Preserved the previously live-verified chain as
  post-exploitation rather than privesc. The RAG Data Service Agent's GA role has project-wide
  Storage get/list; `ragFiles.import` plus `ragCorpora.query` can ingest then recover chunks without
  direct caller Storage access. Viewer alone can query already indexed corpora. Import can also
  poison grounding, but this is not labeled automatic code execution.
- **Feature View data reads.** Current `roles/aiplatform.viewer` contains
  `featureViews.fetchFeatureValues` and `searchNearestEntities`; these return served values and
  neighbors, not merely metadata. Reciprocal review separated regional Bigtable fetches from
  dedicated-endpoint Optimized embedding search; Bigtable does not support embeddings, and
  Optimized online serving is deprecated with a 2027-02-17 shutdown. The official audit catalog
  currently omits both methods, so the book marks audit class/default as undocumented rather than
  asserting silence.

### Material removals and corrections

- Removed the third-party Agent Engine producer-project, tenant-project, metadata-token,
  `code.pkl`, and Workspace-scope narrative. Those claims describe historical managed-runtime
  behavior and an old external report, not a current official expected-feature contract. Current
  Agent Engine custom/default runtime identity chains remain on the privesc page.
- Promoted the default Custom Code Service Agent impact: its current project-level managed role
  includes `iam.serviceAccounts.getAccessToken`, OpenID token/signing and implicit-delegation
  permissions. A no-`actAs` custom training workload can therefore mint another same-project
  service account's token when normal bindings and no deny/PAB prevent it. `GenerateAccessToken` is
  IAM Credentials Data Access and is off by default unless enabled through IAM/all-services audit
  configuration.
- Corrected the enum path for a CustomJob runtime identity from
  `jobSpec.workerPoolSpecs[0].serviceAccount` to `jobSpec.serviceAccount`, removed model upload from
  the list of runtime-account selection points, and added current RAG identity/resource inventory.
- Destructive deletion, endpoint disruption, index removal, and quota exhaustion remain excluded
  as availability-only actions.
- No standalone Vertex AI persistence or unauthenticated page existed. Recurring notebook/pipeline
  schedules, long-lived Agent Engine deployments, endpoint containers, and Workbench startup
  scripts are durable forms of the same already documented run-as primitives, so a second page
  would duplicate rather than add an authorization boundary. No current official anonymous Vertex
  AI resource/data API was identified; public prediction endpoints still enforce their documented
  endpoint/network and authorization configuration.
