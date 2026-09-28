# Vertex Ai — tested

Vertex AI. 12 retained privesc techniques; post-ex generalised pipeline-spec disclosure across the family.

## VERIFIED LIVE — RAG Engine confused-deputy
- CreateRagCorpus (LRO) → `ragFiles:import` (importedRagFilesCount=1) → `:retrieveContexts` returned
  the object plaintext verbatim. `ragCorpora.query` read-back is in `roles/aiplatform.viewer` (low
  priv). Audit: CreateRagCorpus/DeleteRagCorpus = ADMIN_WRITE (always on); ImportRagFiles +
  RetrieveContexts produced NO activity entry (Data Access off by default) — ingest/read-back silent.
  Infra torn down.

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
  code-execution path. Its impact is bounded to the agent's current managed role and bindings; it
  must not be described as Owner without enumeration.
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
