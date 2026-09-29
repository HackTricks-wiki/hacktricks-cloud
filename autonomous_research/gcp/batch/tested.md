# Batch — tested and reviewed

## 2026-09-28 — privilege-escalation audit

Documentation, local stable-gcloud help, role descriptions, and installed CLI-source review only. No Batch job, VM, IAM binding, API, network, or service account was created or changed.

### Retained primitive

- A caller with `batch.jobs.create` on a project and `iam.serviceAccounts.actAs` on a stronger service account can submit attacker-controlled script or container code as that account.
- If no custom account is specified, Batch uses the Compute Engine default service account, but the caller still needs `actAs`. Its roles are environment-specific; Editor is historical/default behavior, not a safe current assumption.
- The runtime service account needs `batch.states.report` on the job project. Logs Writer is only needed when Cloud Logging is enabled, not for job execution itself.
- Code on the job VM can reach its attached account through the metadata server. `secretVariables` and network placement are consequences of that same code-execution primitive, not independent privilege-escalation techniques.

### Removed or folded claims

- Folded public-container execution, Secret Manager injection, and network positioning into the single run-as-service-account primitive.
- Removed read-only job-spec reconnaissance and interpreter environment-variable injection from the privesc page; neither independently crosses a privilege boundary.
- Removed the claim that every custom account needs Logs Writer and that the default Compute account necessarily has Editor.
- Kept Batch scheduling out: Batch submission is one-shot; external orchestration is a separate persistence mechanism.

### Telemetry corrections

- `google.cloud.batch.v1.BatchService.CreateJob` is non-LRO `DATA_WRITE` Data Access and is off by default. `DeleteJob` is a Data Access LRO.
- `ReportAgentState` is explicitly excluded from Cloud Audit Logs.
- Cloud task/agent logs exist only when `logsPolicy.destination: CLOUD_LOGGING` is configured and writable.
- Underlying Compute VM insert/delete calls are Admin Activity LROs and can remain visible even when Batch Data Access and task logging are off. This prevents an “invisible by default” claim.
- Metadata-server token issuance has no token-mint audit event; use of the token follows each target service's logging contract.

Official sources:

- https://docs.cloud.google.com/batch/docs/create-run-job-custom-service-account
- https://docs.cloud.google.com/batch/docs/get-started
- https://docs.cloud.google.com/batch/docs/troubleshooting
- https://docs.cloud.google.com/batch/docs/audit-logging
- https://docs.cloud.google.com/batch/docs/analyze-job-using-logs
- https://docs.cloud.google.com/compute/docs/logging/audit-logging
