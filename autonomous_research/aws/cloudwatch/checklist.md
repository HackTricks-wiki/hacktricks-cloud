# CloudWatch / CloudWatch Logs attack ideas

- [x] CloudWatch Logs `CreateScheduledQuery`: both passed-role gates and recurring S3 result delivery verified end to end. Published in the CloudWatch enum page and PassRole matrix.
- [ ] `UpdateScheduledQuery`: verify role/destination repointing and whether omitted optional fields are cleared under replacement semantics.
- [ ] Cross-account S3 scheduled-query delivery: use a second account only after explicit authorization; verify bucket-owner/event attribution.
- [ ] Scheduled-query lookup-table destination: test destination-role PassRole and whether a malicious refresh can poison downstream investigations/queries.
- [ ] Log Alarm managed scheduled query: test whether alarm mutations indirectly replace/query sources without direct scheduled-query permissions.
