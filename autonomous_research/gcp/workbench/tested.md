# Workbench and Colab Enterprise — tested and researched

## 2026-09-28 — scheduled-execution retained-identity closure

- Legacy `notebooks.googleapis.com` schedules expose create/get/list/delete/trigger but no PATCH. Current Workbench and Colab scheduling uses Vertex AI `Schedule` resources, whose generic PATCH does not establish that every embedded job field is mutable.
- Current gcloud exposes only display, timing, run-count and concurrency fields for schedule update; its source defers notebook-execution updates until the API supports them. The current Terraform Colab schedule resource marks the complete `createNotebookExecutionJobRequest` `ForceNew` and never adds it to the update mask. `NotebookExecutionJob` itself has no PATCH method.
- The embedded request can select notebook source, runtime image/custom container and either `executionUser` or `serviceAccount`, but supported clients treat that request as immutable. Google also requires the named user to modify/trigger a personal-credential schedule and `iam.serviceAccounts.actAs` to modify/trigger a service-account schedule.
- Existing lab Admin Activity history independently records `aiplatform.schedules.create` and `aiplatform.pipelineJobs.create` followed by a separate actAs authorization check on the selected service account. No runtime was launched for this review.
- `gcloud auth application-default login` stores user ADC on the current runtime VM; ADC is not a Schedule field and is deleted with the runtime. The retained-user-ADC update model is invalid.
- Conclusion: the lead is currently unsupported and documented gated, not a book technique or zero-day. Keep only a regression-only raw update-mask negative test, and stop before execution.
