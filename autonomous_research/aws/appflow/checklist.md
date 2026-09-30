# AppFlow — candidate checklist

- [ ] Safely build a disposable Lambda-backed custom connector and test whether `RegisterConnector` + `CreateConnectorProfile` creates a useful capture boundary. Requires a dedicated review of custom-connector Lambda invocation authority and cleanup.
- [ ] Test `UpdateConnectorProfile` end-to-end with a disposable external SaaS tenant: destination-profile replacement for exfiltration and source-profile replacement for data poisoning.
- [ ] Test `ListConnectorEntities` and `DescribeConnectorEntity` against a disposable profile with only exact profile permissions; measure remote audit telemetry and recon value.
- [ ] Test EventBridge partner-source association and the greater-than-256-KB S3 pointer path with a disposable Salesforce developer tenant. Do not model it as an arbitrary cross-account event-bus destination.
- [ ] Test `metadataCatalogConfig` with a disposable Glue role/catalog to determine the exact `iam:PassRole`, Glue, and AppFlow permission set and whether catalog mutation has worthwhile post-exploitation value.
- [ ] Validate Redshift Serverless Data API profile role boundaries and whether updating only profile properties can switch clusters/workgroups without replacing credentials.
- [ ] Validate Snowflake intermediate-stage/KMS policy failure modes with a disposable Snowflake account.
- [x] S3 `UpdateFlow` endpoint/prefix repoint: blocked by service validation.
- [x] S3 `UpdateFlow` task and trigger mutation: succeeds with exact flow permission plus direct S3 validation reads; scheduled update remains `Draft` until `StartFlow`.
- [x] S3 `CreateFlow` minimum-permission retest: requires direct S3 validation reads plus KMS list/describe/grant permissions even with the default AppFlow KMS key.
- [x] Cross-account S3 hypothesis: not supported by AppFlow; keep as a documented boundary rather than an attack.
