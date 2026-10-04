# CloudWatch Omni integration audit — 2026-10-01

## Result

Verified a useful expected-functionality post-exploitation primitive: exact-resource `cloudwatch:UpdateIntegration` can replace an external-agent API key and provider attributes without reading the old credential or receiving Secrets Manager/KMS access. Published this narrowly as integration rebinding/disruption, not credential disclosure or IAM privilege escalation.

No unexpected AWS security defect was found and no private report was created.

## Live authorization results

### External-agent credential and catalog replacement

- `cloudwatch:CreateIntegration` on `arn:aws:cloudwatch:us-east-1:228478051196:integration/*` created an account-scoped `EXTERNAL_AGENT` integration without list/get, secret, KMS, PassRole or space permission.
- This integration type required `integrationAttributes.catalogId`. An arbitrary test string was accepted without existence validation, together with a dummy API key, and the integration became `ACTIVE`.
- `cloudwatch:UpdateIntegration` on the exact generated integration ARN replaced both the API key and `catalogId` without any other positive permission.
- `GetIntegration` and `ListIntegrations` returned the provider type, `authType: API_KEY` and new `catalogId`; neither returned the API key or a `credentialArn`.
- Secrets Manager inventory before and after contained no matching `cw-omni-*` or test secret. Do not generalize the optional API `credentialArn` field to every provider.

The control plane proves credential/configuration replacement. No real third-party agent provider or Slack workspace was connected, so public impact is deliberately conditional on the attacker possessing a valid provider credential and on a victim workflow actually invoking the integration. Raw telemetry export and old-secret recovery are not claimed.

### Role-backed AWS integrations

- Creating an `AWS_INTEGRATION` with `cloudwatch:CreateIntegration` but no PassRole failed specifically on `iam:PassRole` for the supplied role.
- Adding exact-role `iam:PassRole` with `iam:PassedToService=cloudwatch.amazonaws.com` created an `ACTIVE` integration.
- An exact-integration `UpdateIntegration` caller without PassRole was denied specifically on the replacement role. Adding exact-role PassRole succeeded and changed `roleArn`.
- The current AWS-managed `CloudWatchOmniAWSIntegrationPolicy` defines this path as Context Graph resource discovery. The test did not return STS credentials or show arbitrary action selection, so it is recorded as a guardrail rather than a privilege-escalation technique.
- Only one account-scoped `AWS_INTEGRATION` was accepted; a second create returned a type-level conflict.

## CloudTrail

Successful `CreateIntegration` and `UpdateIntegration` operations were default management writes with `eventSource: cloudwatch.amazonaws.com`.

- Provider API keys were recorded as `HIDDEN_DUE_TO_SECURITY_REASONS`.
- `catalogId`, role ARN and integration identifier were retained in clear.
- Successful create/update generated two records at the same time: a caller-attributed event with the full sanitized integration response and a service-internal companion with `userIdentity: null`, flattened account scope and compact status.
- IAM-denied update attempts had null request parameters and described the missing action or PassRole in the error.

## Rejected or deferred claims

| Idea | Disposition |
| --- | --- |
| Read the stored provider API key through `GetIntegration` | Rejected; only auth type and attributes were returned |
| Find the API key in a customer-visible Secrets Manager secret | Rejected for the tested external-agent path; no matching secret existed and no ARN was returned |
| Treat arbitrary `catalogId` acceptance as an IDOR | Rejected; creation-time non-validation alone showed no foreign catalog access or data return |
| Treat role replacement as generic PassRole escalation | Rejected; documented service use is bounded resource discovery and no credentials were returned |
| Claim Slack/provider traffic interception unconditionally | Rejected; requires valid provider credentials and a real downstream workflow, neither of which was provisioned |

## Cleanup

All test integrations and every `ht-omni-awsint-*` / `ht-omni-upd-*` IAM role were deleted. One AWS integration was briefly left after a cleanup parser used `.integrationId` instead of the response's nested `.integration.integrationId`; an independent inventory detected it immediately and it was explicitly deleted. Final `ListIntegrations`, matching IAM-role inventory and matching Secrets Manager inventory were empty. No domain, space, alert, telemetry-forwarding, compute or third-party resource was created for this audit.
