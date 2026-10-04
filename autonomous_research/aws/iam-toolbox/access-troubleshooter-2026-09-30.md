# IAM Toolbox Access Troubleshooter audit — 2026-09-30

## Result

Verified the new public-preview `iam-toolbox:GetRequestAuthorizationDetails` cross-principal authorization-snapshot behavior. This is expected AWS functionality and was added to IAM enumeration/post-exploitation coverage, not reported as a vulnerability.

## Model and documented boundaries

- API model: `iam-toolbox` `2018-05-10`; signing name and IAM action namespace remain `iam`.
- Single operation: `GetRequestAuthorizationDetails`.
- Required permission: `iam:GetRequestAuthorizationDetails` on `*`.
- Input: an authorization ID returned by a supported AccessDenied error.
- Snapshot retention: at least 24 hours; creation is asynchronous.
- Reader: any principal with the action in the same account/organization, not only the denied principal. Cross-organization calls return only the reader organization's policy/context portion.
- Current supported service list is primarily most IAM APIs; authorization IDs are not guaranteed for every denial.

## Live exact-action test

1. Created disposable user `ht-iamtb-denied-20260930` with one inline policy, `HTExplicitDenyCanary`, whose named statement `HTExplicitDenyCanary` explicitly denied `iam:GetUser` on that exact user.
2. Created a temporary access key, waited for propagation and called the denied getter. The AccessDenied response contained a live authorization ID (redacted from this ledger).
3. Assumed `ChackBotAdministratorRole` from the authorized source profile with a session policy containing only `iam:GetRequestAuthorizationDetails` on `*`.
4. The first two reads returned `ResourceNotFoundException`; the third succeeded after asynchronous propagation.
5. The snapshot disclosed the denied user's ARN/ID, source IP, user agent, requested Region/time, organization ID/root/OU path, exact `iam:GetUser` action/resource, explicit-deny result, inline policy opaque ID/attachment, named deny statement, all evaluated SCP IDs/types and their root/OU/account attachments, and the AWS-managed `FullAWSAccess` matching allow statement.
6. The same session was denied `iam:ListUsers`, confirming that ordinary IAM enumeration was absent.
7. A second session without `iam:GetRequestAuthorizationDetails` received `AccessDeniedException` for the same ID.
8. After deleting the access key, inline policy and user, a fresh exact-action session still retrieved the same snapshot. The result is historical and not invalidated by fixture deletion.
9. CloudTrail later indexed the denied `GetUser` event and retained the complete AccessDenied `errorMessage`, including the authorization ID. A fresh session limited to `cloudtrail:LookupEvents` plus `iam:GetRequestAuthorizationDetails` harvested that ID from Event History and retrieved the snapshot while still being denied `iam:ListUsers`.

The response did not contain any policy JSON. Inline policies were opaque identifiers; SCPs exposed policy/attachment ARNs and matched statement IDs/effects only.

## Telemetry

- The original denial was returned directly to the caller with the authorization ID. Such strings are likely to be copied into CI/application logs, tickets, chat and shell history.
- The default `iam.amazonaws.com` `GetUser` management event preserved the entire denied `errorMessage` and usable ID. `cloudtrail:LookupEvents` therefore provides an independent harvesting path but creates its own management read event.
- After ordinary delivery delay, CloudTrail indexed successful, not-yet-materialized and unauthorized toolbox reads as default read-only management events under `iam-toolbox.amazonaws.com`.
- The event retained the full `authorizationId`, caller, source IP/user agent and Region. Successful responses had null `responseElements`, so the disclosed policy/context snapshot was not copied into the event.

## Cleanup

The disposable access key was deleted before the inline policy and user. Exact `GetUser` and `ListAccessKeys` checks then returned `NoSuchEntity`. No role, group, managed policy, login profile, MFA device, organization policy or non-IAM resource was created. Final fixture residue is zero.
