# Cognito replica resilience-destruction audit — 2026-09-30

## Result

Shipped the expected two-stage availability attack against Cognito multi-Region replication. `UpdateUserPoolReplica` can set the only secondary replica to `INACTIVE`; `DeleteUserPoolReplica` can then delete that inactive secondary. The primary directory and users remain, so this is resilience destruction rather than directory deletion or privilege escalation.

The immediate effect of `INACTIVE` is to remove the secondary's authentication/session operations. Direct API clients routed there fail, and failover cannot authenticate users there. Deletion removes the replica completely. Recovery requires creating a new paid replica with the primary pool's multi-Region KMS prerequisite, waiting for synchronization, restoring Region-specific WAF/Lambda/messaging/logging settings, and activating it.

## Safe exact-resource authorization probes

No multi-Region pool existed, so every write targeted the previously confirmed nonexistent ID `us-east-1_A1b2C3d4E`. No live replica was changed.

For `UpdateUserPoolReplica`, the same request targeted `RegionName=eu-west-1` and `Status=INACTIVE`:

- Called through `us-east-1`, a session with only the action on `arn:aws:cognito-idp:us-east-1:228478051196:userpool/us-east-1_A1b2C3d4E` reached `ResourceNotFoundException`; a policy containing only the equivalent `eu-west-1` ARN was denied.
- Called through `eu-west-1`, the result reversed: the exact `eu-west-1` ARN reached not-found and the `us-east-1` ARN was denied.

This proves that IAM constructs the resource ARN with the API endpoint's Region, not the target `RegionName`. It matches the documented ability to invoke the update from either primary or secondary.

`DeleteUserPoolReplica` must be called from the primary and requires the secondary to be inactive. A session with only that action on the exact synthetic `us-east-1` pool ARN reached not-found from the primary endpoint; the same action scoped only to the secondary-Region ARN was denied. No list/describe or other permission was present.

## `DescribeTermsByClient` exclusion

The remaining new read API was deliberately not added as an attack. Its response contains app-client identifiers and localized Terms of use/Privacy policy links that managed login displays publicly during sign-up after both documents are configured. It does not return the document contents, user data, credentials, or an enforcement bypass.

The unusual documented dependent permission was live-confirmed on the same synthetic exact pool ARN: `DescribeTermsByClient` alone was denied specifically for missing `cognito-idp:DescribeTerms`; adding both exact-pool reads reached `ResourceNotFoundException`. This is a secure restriction and low-value enumeration, so publishing it would add noise rather than a useful technique.

## Telemetry

CloudTrail indexed both replica APIs as `readOnly:false` management events under `cognito-idp.amazonaws.com`. Service-reached update failures retained `userPoolId`, `regionName`, and `status`; delete retained the first two fields. IAM denials omitted request parameters and responses but exposed the endpoint-Region ARN in the error.

Overall stealth: **Low** for a real status change/deletion because both writes are rare and explicit.

## Cleanup

Only calls against a confirmed nonexistent synthetic pool and expiring restricted STS sessions were used. Final user-pool inventories in `us-east-1` and `eu-west-1` remained empty. No user pool, replica, KMS object, Route 53 health check, domain, WAF association, trigger, log delivery, role or policy was created.

## Sources

- https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-multi-region.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_UpdateUserPoolReplica.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DeleteUserPoolReplica.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeTermsByClient.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-managed-login.html#cognito-user-pools-managed-login-terms-documents
