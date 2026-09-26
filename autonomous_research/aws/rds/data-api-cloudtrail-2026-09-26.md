# Aurora RDS Data API CloudTrail audit — 2026-09-26

## Finding

The [AWS Aurora Data API CloudTrail guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/logging-using-cloudtrail-data-api.html) explicitly classifies `BatchExecuteStatement`, `BeginTransaction`, `CommitTransaction`, `ExecuteStatement`, and `RollbackTransaction` as **opt-in data events** on `AWS::RDS::DBCluster`. Its `ExecuteStatement` example redacts the SQL text, database, and schema. The previous book said all RDS calls were management events and placed `ExecuteStatement` in a default-management-event table. That was incorrect. RDS control-plane API calls remain default management events; direct database-protocol SQL is outside CloudTrail and requires engine auditing for statement visibility.

## Book corrections

- Corrected 17 repeated blanket statements in RDS post exploitation.
- Reclassified `ExecuteStatement` in the Data API technique's logging table and corrected its detection text.
- Added CloudTrail guidance to RDS service enumeration and a stealth rating to the affected technique.

## Candidate tests and future work

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| Enable HTTP endpoint and run SQL via Data API from outside the VPC | Expected | Previously covered in book | Confirm least IAM scope and data-event payload against a temporary Aurora fixture only if needed |
| Query text in CloudTrail data event despite documented redaction | Potential unexpected | No evidence; do not report | Check a controlled statement with enabled selector; remove fixture afterwards |
| Data API event missing despite matching `AWS::RDS::DBCluster` selector | Potential unexpected | No evidence | Verify selector, Region, and destination before treating as a service defect |

No AWS resources were created or left running in this documentation audit. No zero-day claim.
