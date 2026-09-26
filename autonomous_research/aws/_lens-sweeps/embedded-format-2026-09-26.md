# Embedded AWS technique format sweep — 2026-09-26

A heading scan of `aws-services/` identified offensive techniques embedded inside enumeration pages that escaped the earlier dedicated privesc/post-exploitation/persistence retrofit. Many apparent gaps are only reference headings to dedicated pages; the entries below contain actual steps and had missing required fields.

| Page / technique | Gap filled | Evidence or limit |
| --- | --- | --- |
| AppFabric ingestion destination | Stealth | Existing control-plane log table shows destination in `CreateIngestionDestination` |
| Connect Customer Profiles event stream | Stealth | Existing `CreateEventStream` log table identifies destination Kinesis ARN |
| Amazon Connect storage config | Explicit impact and stealth | Existing log table identifies `StorageConfig` destination |
| Deadline queue/fleet role vending | Stealth for both privesc variants | Existing live minimum-permission test and log tables retained |
| Private CA Connector for SCEP challenge read/create | Stealth; corrected `GetChallengePassword` Event History default | [AWS SCEP CloudTrail guide](https://docs.aws.amazon.com/privateca/latest/userguide/logging-using-cloudtrail-c4scep.html) lists both as management events; custom trails may omit read management events |
| Device Farm project variables, live session endpoint, artifacts | Impact/stealth/log tables as applicable | [AWS Device Farm CloudTrail guide](https://docs.aws.amazon.com/devicefarm/latest/developerguide/logging-using-cloudtrail.html) covers API calls. Endpoint use remains conditional on endpoint authorization; artifact URL retrieval was previously confirmed by HTTP 200. |
| CodeArtifact known-asset read, package publish, repository policy backdoor | Impact/stealth/log tables and persistence scope | [AWS CodeArtifact CloudTrail guide](https://docs.aws.amazon.com/codeartifact/latest/ug/codeartifact-information-in-cloudtrail.html) confirms API and package-client calls, including cross-account log delivery |
| Neptune Database read/query and stream; Neptune Analytics query | Impact/stealth/log tables | [Neptune DB CloudTrail guide](https://docs.aws.amazon.com/neptune/latest/userguide/cloudtrail.CloudTrail.html) limits CloudTrail to management calls; [database audit guide](https://docs.aws.amazon.com/neptune/latest/userguide/auditing.html) shows audit logs are off by default; [Analytics CloudTrail guide](https://docs.aws.amazon.com/neptune-analytics/latest/userguide/monitoring-cloudtrail-info.html) classifies `ExecuteQuery` as an optional data event |
| Security IR and Systems Manager Incident Manager | Stealth for embedded incident-response actions; response-plan persistence scope | Existing management-event tables; corrected an absolute claim about presigned URL downloads because storage-owner telemetry may exist |
| VPC Lattice invocation, VPC association, access-log subscription | Impact/stealth/log fields | [AWS CloudTrail guide](https://docs.aws.amazon.com/vpc-lattice/latest/ug/monitoring-cloudtrail.html) covers control plane; [access-log guide](https://docs.aws.amazon.com/vpc-lattice/latest/ug/monitoring-access-logs.html) says request logs are optional and disabled by default |

Follow-up factual checks: [CodeArtifact repository-policy docs](https://docs.aws.amazon.com/codeartifact/latest/ug/repo-policies.html) require an external identity-policy allow and a domain-policy `GetAuthorizationToken` grant for package-manager access. Direct known-asset API reads use their own authorization path. [Incident Manager's availability notice](https://docs.aws.amazon.com/incident-manager/latest/userguide/incident-manager-availability-change.html) limits these techniques to existing enabled customers since November 7, 2025.

Dedicated privesc retrofit continues beyond the embedded-page sweep:

| Page | Fields and corrections | Evidence |
| --- | --- | --- |
| Secrets Manager privesc | Stealth for `GetSecretValue` and resource-policy self-grant; qualified the extra KMS `Decrypt` detection signal | [Secrets Manager CloudTrail guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/monitoring-cloudtrail.html); [KMS CloudTrail guide](https://docs.aws.amazon.com/kms/latest/developerguide/logging-using-cloudtrail.html) permits KMS event exclusion on a trail |
| KMS privesc | Stealth for key-policy edit, grant, replication and decrypt; narrowed impact to obtainable ciphertext, required context and service permissions | [KMS Decrypt API](https://docs.aws.amazon.com/kms/latest/APIReference/API_Decrypt.html); [encryption context](https://docs.aws.amazon.com/kms/latest/developerguide/encrypt_context.html) |
| Lambda privesc | Stealth for 18 existing variants; corrected the absolute `Invoke` invisibility and `GetFunction` archive-download logging claims | [Lambda CloudTrail guide](https://docs.aws.amazon.com/lambda/latest/dg/logging-using-cloudtrail.html) separates management from optional `Invoke` data events; [function URL monitoring](https://docs.aws.amazon.com/lambda/latest/dg/urls-monitoring.html) covers URL data events |
| Identity Center, Payment Cryptography, Storage Gateway post-exploitation | Stealth for account lockout, payment-key export, and file-share privilege abuse | Existing log tables; [Payment Cryptography CloudTrail guide](https://docs.aws.amazon.com/payment-cryptography/latest/userguide/monitoring-cloudtrail.html) classifies key export as control plane |

No new cloud infrastructure was launched for this format sweep. Continue scanning actual embedded techniques while excluding reference-only headings.
