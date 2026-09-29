# CloudWatch / CloudWatch Logs attack ideas

- [x] CloudWatch Logs `CreateScheduledQuery`: both passed-role gates and recurring S3 result delivery verified end to end. Published in the CloudWatch enum page and PassRole matrix.
- [x] Observability Admin `CreateS3TableIntegration` + Logs source association: verified role-mediated future-log delivery, API-vs-console wildcard behavior, hidden `GetS3TableIntegration` dependency, independent table-read gates, and zero-residue cleanup. Published in the CloudWatch enum page; evidence in `s3-table-integration-passrole-2026-09-26.md`.
- [x] Observability Admin telemetry-pipeline destructive processors: `TestTelemetryPipeline` proved complete event dropping and field/severity rewriting; a zero-match live metrics pipeline proved update behavior and the exact `cloudwatch:PutPipelineRule` dependency. Published in enum/post-exploitation; evidence in `telemetry-pipeline-update-2026-09-29.md`.
- [ ] Telemetry-pipeline credential relay: test whether updating a Palo Alto hostname or ServiceNow instance URL makes the service send a canary Secrets Manager credential to an attacker-controlled HTTPS endpoint. Use only a disposable canary secret/role/pipeline and capture no real credentials.
- [ ] `UpdateScheduledQuery`: verify role/destination repointing and whether omitted optional fields are cleared under replacement semantics.
- [ ] Cross-account S3 scheduled-query delivery: use a second account only after explicit authorization; verify bucket-owner/event attribution.
- [ ] Scheduled-query lookup-table destination: test destination-role PassRole and whether a malicious refresh can poison downstream investigations/queries.
- [ ] Log Alarm managed scheduled query: test whether alarm mutations indirectly replace/query sources without direct scheduled-query permissions.
