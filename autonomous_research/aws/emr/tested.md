# EMR (serverless / on-EKS) — tested/documented

## Coverage on aws-emr-serverless-privesc page
- StartJobRun + iam:PassRole (Spark/Hive arbitrary code as executionRoleArn) — VERIFIED (pre-existing).
- UpdateApplication runtimeConfiguration poisoning (env-var RCE, no PassRole) — VERIFIED live emr-7.5.0 (pre-existing).
- ADDED 2026-09-26: `emr-serverless:GetSessionEndpoint` on one exact existing session ARN — VERIFIED end to end cross-principal. A role explicitly denied Get/List/Start/TerminateSession, PassRole, and direct S3 access retrieved the one-hour Spark Connect token, connected to the administrator-created session, and read an execution-role-only S3 canary. No creator binding and no PassRole at redemption. Full evidence and cleanup: `session-endpoint-2026-09-26.md`.
- ADDED 2026-09-25: emr-containers:GetManagedEndpointSessionCredentials + iam:PassRole — interactive Spark session on an EXISTING managed endpoint as the passed executionRoleArn. API takes caller-supplied executionRoleArn (=> PassRole-gated) and returns credentials.token (sensitive) authenticating to JEG/Livy. Notebook flavour of StartJobRun; no new endpoint => stealthier than CreateManagedEndpoint. Doc-grounded from botocore model (in: endpointIdentifier, virtualClusterIdentifier, executionRoleArn, credentialType, durationInSeconds; out: id, credentials{token}, expiresAt). Not lab-fired (needs a running EKS virtual cluster + managed endpoint = costly/slow to stand up); PassRole gate is the same class already verified for CreateManagedEndpoint/StartJobRun.

## Parked
- finspace-data:GetProgrammaticAccessCredentials — vends FinSpace env data-access creds. Very niche service, rarely deployed. Parked, low value.
