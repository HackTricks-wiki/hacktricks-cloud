# Route 53 ARC readiness cross-account authorization audit — 2026-09-30

## Result

Public technique #106 documents `route53-recovery-readiness:CreateCrossAccountAuthorization` as an account-wide, service-limited persistence and reconnaissance primitive. The write stores an external AWS account-root ARN. That account can add supported resources owned by the authorizing account to central resource sets and continuously inspect their readiness-rule results.

The authorization is broader than a conventional per-resource share: the request selects an account, not resources, and the service defines no destination-account condition key or resource-level ARN for the action. The receiver still needs known supported victim resource ARNs, central-account readiness permissions, and access to the legacy readiness-check feature. It receives no AWS credentials, direct native service permissions, workload data, or mutation capability.

## Live validation

Initial inventory in `us-west-2` found zero cross-account authorizations, resource sets, readiness checks, cells, and recovery groups. The readiness service-linked role was absent.

A temporary principal with only `route53-recovery-readiness:CreateCrossAccountAuthorization` on `*` was rejected before authorization creation with:

```text
Cannot create the service-linked role. Make sure that the iam:CreateServiceLinkedRole permission is present in the IAM policy so that we can create the service-linked role.
```

A fresh temporary principal was then granted:

- `route53-recovery-readiness:CreateCrossAccountAuthorization` on `*`
- `iam:CreateServiceLinkedRole` only on `arn:aws:iam::*:role/aws-service-role/route53-recovery-readiness.amazonaws.com/AWSServiceRoleForRoute53RecoveryReadiness`, conditioned on `iam:AWSServiceName=route53-recovery-readiness.amazonaws.com`

That principal successfully authorized `arn:aws:iam::418720621023:root`. An administrator independently listed the exact authorization and confirmed creation of `/aws-service-role/route53-recovery-readiness.amazonaws.com/AWSServiceRoleForRoute53RecoveryReadiness`.

The external account did not create a resource set or readiness check, so cross-account rule results and a chosen-comparator oracle were not live measured. Those capabilities are current documented service behavior. The receiver-side feature is no longer open to new customers, which is an important prerequisite.

## Telemetry boundary

AWS documentation says CloudTrail captures all readiness API calls. `cloudtrail:LookupEvents` in the required `us-west-2` Region is explicitly denied by the organization SCP, so exact live event serialization was not retrieved. A permitted `us-east-1` lookup did not return the service-linked-role event during the bounded wait. The public logs table therefore uses documented event names and the request fields, not a claim of independently observed complete payloads.

## Cleanup

Cleanup completed in dependency order:

1. deleted the cross-account authorization;
2. deleted the temporary access key, inline policy, and user;
3. requested deletion of `AWSServiceRoleForRoute53RecoveryReadiness` and waited for the asynchronous task;
4. independently confirmed an empty authorization list, zero `ht-readiness-xacct-*` users, and `NoSuchEntity` for the service-linked role.

No readiness check, resource set, cell, recovery group, application resource, network resource, or compute resource was created. No unexpected AWS behavior or private vulnerability report resulted. The missing first-use dependency in the Service Authorization table is a documentation/operational nuance, not a security boundary bypass.

## Follow-up ideas

- In an explicitly authorized pre-existing readiness customer account, measure which rule messages expose raw values versus only equality/readiness state.
- Use two controlled same-type resources to determine whether repeated comparison checks provide practical inference for Lambda, EBS, SQS, VPC, MSK, and VPN settings.
- Compare victim-account CloudTrail for service-linked-role polling with receiver-account ARC management events.
- Verify whether SCP/RCP or resource policies on supported services can constrain the readiness service-linked role without breaking legitimate checks.

## Sources

- https://docs.aws.amazon.com/r53recovery/latest/dg/recovery-readiness.cross-account.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/readiness-what-is.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/recovery-readiness.rules-resources.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/using-service-linked-roles-readiness.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/Route53RecoveryReadinessServiceRolePolicy.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_route53-recovery-readiness.html
- https://docs.aws.amazon.com/r53recovery/latest/dg/cloudtrail-readiness.html
