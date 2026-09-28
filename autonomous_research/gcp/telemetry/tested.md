# Telemetry API security research ledger

## 2026-09-29 — OTLP log forgery and audit boundary

- Mapped all current `roles/telemetry.*` roles and separated normal collector permissions
  (`logging.logEntries.create`, `monitoring.timeSeries.create`, `telemetry.traces.write`) from beta
  integrated-service permissions (`telemetry.consumers.write*`) and consumer-resource IAM.
- Live-tested an isolated service account with only `roles/telemetry.logsWriter` and
  `roles/serviceusage.serviceUsageConsumer`. After IAM propagation, `POST /v1/logs` succeeded and
  stored an attacker-selected log name, severity, labels, scope, body and monitored-resource
  identity. A synthetic nonexistent instance ID was accepted as a `gce_instance` resource.
- No caller-attributed audit entry appeared under the default policy. A Telemetry-specific
  `DATA_WRITE` audit config was rejected because the service does not support service-level Cloud
  Audit Logs configuration.
- A short `allServices/DATA_WRITE` experiment also produced no Telemetry record, but its Monitoring
  `CreateTimeSeries` positive control produced no Data Access record either. This was treated as
  audit-configuration propagation uncertainty, not proof that OTLP export is permanently
  unauditable. The book claims default silence only. The classic Logging `WriteLogEntries` path
  remains officially documented as never audited.
- Trace ingestion was intentionally not attempted: sending the first trace can create the `_Trace`
  observability bucket, which currently has no supported immediate delete path. Consumer-resource
  IAM endpoints and integrated-service destination semantics remain documentation-poor and were not
  inferred from permission names.
- Cleanup deleted both custom logs and the temporary metric descriptor, explicitly restored the
  original null audit configuration, deleted the service-account key/config/account and both
  project bindings, and removed all response files. Final active-resource/API state matches
  baseline (`telemetry.googleapis.com` remained enabled); descriptor lookup returns 404 and both
  logs return no entries. Monitoring provides no independent time-series deletion operation, so the
  two benign value-`1` points behind the deleted descriptor are inaccessible and age out under
  service retention. Do not use a metric positive control in future zero-data-residue tests.

## Classification

- Arbitrary OTLP log/metric/trace injection is expected writer functionality and belongs in
  HackTricks, not a vulnerability report.
- A protected audit-log-name bypass, cross-project destination bypass, or consumer-IAM confused
  deputy would be private-first. None was claimed or tested in this batch.
