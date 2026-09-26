# AppFlow — tested

## VERIFIED live (lab 228478051196, us-east-1) — 2026-09-25
### appflow:CreateFlow + StartFlow — attacker-defined transfer using stored connector authority  [SHIPPED to wiki]
- Created S3->S3 flow with attacker-chosen source bucket/prefix + attacker-chosen destination bucket/prefix (CreateFlow -> flowStatus Active).
- StartFlow executed; source rows (1,topsecret / 2,alsosecret) landed at s3://<dest>/stolen/<flow>/<execId> as JSON {"id":"1","secret":"topsecret"}...
- End-to-end exfil PROVEN. Min-perms: appflow:CreateFlow + appflow:StartFlow (no iam:PassRole — service-linked role + connector-profile authority). Destination bucket policy allowing appflow.amazonaws.com attached to attacker-OWNED bucket.
- Teardown: delete-flow --force-delete + emptied/deleted both buckets. Residue verified zero.

### UpdateFlow endpoint immutability — VERIFIED constraint (honest calibration)
- UpdateFlow on S3 flow REJECTS changing destination object: ValidationException "Destination object for the destination connector can not be updated".
- Also rejects changing source object: "Do not update the object for the flow."
- => Cannot silently repoint an existing benign flow's endpoints. Offensive vector is CreateFlow (own flow), not UpdateFlow.

## Precondition-gated (documented, not lab-fired)
- SaaS connector profile as source (Salesforce/Snowflake/ServiceNow/Slack/Zendesk/SAPOData/Redshift/Marketo): requires an existing connector profile w/ valid SaaS creds in the account (external cost + creds unavailable). DescribeConnectorProfiles REDACTS credentials but the flow USES them -> exfil SaaS data without knowing creds. High confidence from API model + verified S3 mechanism.
- Reverse (integrity): S3 source (attacker data) -> SaaS destination connector profile = write/inject records into the SaaS business system using stored authority.

## Prior coverage (already on enum page)
- appflow:StartFlow of a pre-existing flow (fixed source/dest) — documented with S3 bucket-policy validator nuance. CreateFlow section added ABOVE it removes the fixed-destination precondition.
