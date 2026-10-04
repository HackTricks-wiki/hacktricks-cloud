# Cognito multi-Region password-lockout splitting — 2026-09-30

## Result

Shipped a bounded unauthenticated technique based on the current Amazon Cognito multi-Region replication contract. An `ACTIVE` secondary supports public `InitiateAuth` and `RespondToAuthChallenge` against its regional endpoint. AWS explicitly documents that password-failure counts are not synchronized between Regions: every replica maintains its own counter.

Cognito normally begins a one-second lockout after five failed password attempts and exponentially increases the delay for further accepted failures up to approximately 15 minutes. With the maximum one secondary replica, a password attacker can distribute failures across two independent counters, obtaining up to five initial failures per replica before each begins backoff and alternating Regions thereafter. This is expected/disclosed product behavior, not an AWS vulnerability.

The security effect can be broader when regional controls drift. AWS allows regional WAF associations, Lambda triggers, log delivery and communications settings to differ. Direct API clients choose the regional Cognito endpoint; an attacker does not have to follow a managed-domain Route 53 health check. Defenders must therefore apply controls and aggregate failures across both Regions.

## Preconditions and boundaries

- The replica must be `ACTIVE`; an `INACTIVE` secondary exposes reads/configuration but not `InitiateAuth`.
- The attacker needs a replicated client ID, username and a compatible password authentication flow. A confidential client still requires its client secret/hash.
- This does not bypass a second factor. TOTP is unsupported in secondary replicas and TOTP-configured users must authenticate in the primary Region.
- Secondary pools cannot create users or perform primary-only profile/password writes. Federated-user failover has additional prior-primary-login constraints.
- Success yields Cognito application tokens and whatever the application/identity pool grants that user, not generic AWS administrator access.

## Safe authorization probe

No multi-Region pool existed in either allowed Region. A restricted session allowed only `cognito-idp:ListUserPoolReplicas` on one synthetic exact user-pool ARN:

```text
arn:aws:cognito-idp:us-east-1:228478051196:userpool/us-east-1_A1b2C3d4E
```

The exact request passed IAM and returned `ResourceNotFoundException`; a different pool ID returned `AccessDeniedException`. An unsigned control returned `MissingAuthenticationTokenException`. This confirms that administrative replica inventory is authenticated and exact-pool resource scoped; it does not test the public authentication behavior, which is established by the current official supported-operation contract.

An end-to-end replica was deliberately not created. MRR requires an Essentials/Plus pool plus a multi-Region customer-managed KMS key, and KMS key deletion has a mandatory waiting period. Creating those fixtures would violate the mission's immediate-cleanup rule. The account remained empty, and the public book does not claim a live lockout race.

## Telemetry

CloudTrail indexed both signed replica-inventory probes as read-only management events under `cognito-idp.amazonaws.com`. The authorized not-found event retained the synthetic `userPoolId`; the denied different-pool event omitted `requestParameters` but exposed the denied pool ARN in `errorMessage`. Both responses were null. Live Cognito testing earlier in the same audit confirmed `InitiateAuth` as a default management event under the same event source. Authentication events retain `awsRegion`, `clientId`, result/error and normal source context while replacing `authParameters` and returned tokens/sessions with `HIDDEN_DUE_TO_SECURITY_REASONS`. Regional `AWS/Cognito` `SignInSuccesses` metrics allow failures to be calculated from `SampleCount - Sum` for a pool/client. WAF request logs require regional WAF logging configuration.

Overall stealth: **Low** because guessing is noisy, but per-Region alerting can undercount the combined attack.

## Cleanup

Only read-only synthetic-ID calls and an expiring restricted STS session were used. Final user-pool inventories in `us-east-1` and `eu-west-1` are empty. No user pool, replica, KMS key/alias/grant, app client, user, domain, Route 53 health check, WAF association, Lambda trigger, log destination, IAM role/policy or other resource was created.

## Sources

- https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-multi-region.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/authentication.html#authentication-flow-lockout-behavior
- https://docs.aws.amazon.com/cognito/latest/developerguide/logging-using-cloudtrail.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/metrics-for-cognito-user-pools.html
- https://aws.amazon.com/cognito/pricing/
