# CodeCatalyst `CreateAccessToken` — assessed 2026-09-26

## Verdict

Real CodeCatalyst developer-identity persistence, but a reasoned exclusion from the public AWS IAM
technique catalog. A compromised CodeCatalyst Builder ID or IAM Identity Center SSO session can call
`CreateAccessToken` and retain the returned personal access token (PAT) after the creating browser or
OIDC session expires. The PAT is an application-specific password for CodeCatalyst Git, IDE, and
package access; it is not documented as a replacement for the bearer credential used by the
CodeCatalyst CLI/API and it does not create AWS IAM credentials.

This can still support source exfiltration, source/package modification, dependency poisoning, or an
indirect workflow trigger, subject to the victim's existing project roles, branch rules, workflow
configuration, and connected-role controls. It creates no new authorization: the token represents
the same user across every CodeCatalyst space and project where that identity is already a member.
Its security value is extending the access window, not crossing an IAM privilege boundary.

CodeCatalyst stopped accepting new customers on 2025-11-07. Existing customers can continue using
existing spaces but cannot create new spaces, and AWS says it does not plan new features. AWS has not
published an end-of-support date. That lifecycle plus the separate identity plane makes a new public
HackTricks page disproportionate without a verified existing deployment.

## Authorization plane

The installed AWS CLI 2.34.45 model declares the CodeCatalyst service's signature version as
`bearer` and its endpoint as global. AWS's CLI setup requires an SSO session with the registration
scope `codecatalyst:read_write`; the active Builder ID or federated Identity Center user becomes the
"current user" for `CreateAccessToken`.

There is no identity-policy equivalent of `codecatalyst:CreateAccessToken`. The current Service
Authorization Reference says CodeCatalyst has no directly invocable IAM API actions; it lists only
permission-only IAM actions for AWS-account connections, billing, space creation, and Identity
Center application administration. Those IAM permissions do not authorize the bearer API's
`CreateAccessToken`. CodeCatalyst roles and the user identity authorize it instead.

The request has no `spaceName`, project, resource ARN, permission/scope list, or IAM role input:

```json
{
  "name": "descriptive-name",
  "expiresTime": "RFC3339 timestamp (optional)"
}
```

## Secret, scope, lifetime, and revocation

- Successful creation returns `secret`, `accessTokenId`, `name`, and `expiresTime`; the current model
  marks `secret` sensitive. The secret is displayed only once and cannot be retrieved later.
- If `expiresTime` is omitted, the default is one year from creation. The API accepts a caller-supplied
  RFC 3339 timestamp, but current official documentation and the model publish no maximum custom
  lifetime. Therefore do not describe the token as capped at one year.
- The token is associated with the user identity across all of that identity's CodeCatalyst spaces
  and projects. There are no token-level scopes in the create request. Space/project roles and
  resource controls continue to decide read, write, push, or package-publish access.
- Official examples establish PAT use as the password for CodeCatalyst Git and as authentication for
  package repositories; the general documentation also mentions IDE access. They do not establish
  that a PAT can authenticate the bearer-only CodeCatalyst management API.
- A user can have at most 100 PATs. `ListAccessTokens` returns only ID, name, and expiry for the
  calling identity, never the secret. Expired tokens are deleted and stop appearing.
- `DeleteAccessToken` revokes one token and AWS says only the user who created it can delete it.
  Current docs expose no space-administrator API to enumerate or delete every member's PAT.

The persistence statement is an inference from the documented credential model: the PAT is a
separate password-like credential with its own expiry and is used without the original SSO login,
so it can outlive the session that created it. AWS does **not** document whether password reset,
Builder ID disablement, Identity Center disablement, space removal, or administrative session
revocation invalidates an already-issued PAT. Do not claim survival across those identity-lifecycle
events. A PAT also is not documented as able to call `CreateAccessToken`, so it should not be treated
as self-renewing persistence.

## Audit visibility

CodeCatalyst documents two audit paths for space/project activity:

- CloudTrail management events are written to the space's designated billing account and are
  available in Event History for 90 days or longer through a trail.
- A Space administrator can call `ListEventLogs` for a specific space; this guarantees 30 days and
  includes event/user/source/request metadata.

However, `CreateAccessToken`, `ListAccessTokens`, and `DeleteAccessToken` are global user-profile
operations with no space parameter. AWS's CloudTrail page does not specifically list or illustrate
these operations, and the per-space event API cannot unambiguously assign a cross-space PAT event to
one billing account. Without a live disposable identity, central logging for PAT creation/deletion
remains unverified. Do not assert that these events are either definitely present or definitely
absent in CloudTrail. The reliable documented detection surface is the user's own PAT inventory
(token ID/name/expiry), plus repository/package activity and membership changes in each affected
space.

## Lab preflight and residue

- `ht-admin` is an AWS IAM assumed role, not a CodeCatalyst bearer identity.
- No local CodeCatalyst CLI profile, CodeCatalyst/SSO environment variable, or IAM Identity Center
  instance exists in account `228478051196`.
- CloudTrail Event History in the SCP-allowed `us-east-1` and `eu-west-1` Regions contained no
  `CreateAccessToken` or `codecatalyst.amazonaws.com` events. The organization's Region SCP denied
  the same read-only lookup in `us-west-2`, CodeCatalyst's historical home Region.
- No `aws sso login`, space/profile creation, PAT creation, or external identity action was
  attempted. No secret was returned or stored; cleanup was unnecessary and residue is zero.

## Primary sources

- Service lifecycle and migration: https://docs.aws.amazon.com/codecatalyst/latest/userguide/migration.html
- `CreateAccessToken`: https://docs.aws.amazon.com/codecatalyst/latest/APIReference/API_CreateAccessToken.html
- PAT creation, inventory, expiry, and deletion: https://docs.aws.amazon.com/codecatalyst/latest/userguide/ipa-tokens-keys.html
- CodeCatalyst identity and PAT concepts: https://docs.aws.amazon.com/codecatalyst/latest/userguide/concepts.html
- CLI bearer/SSO configuration: https://docs.aws.amazon.com/codecatalyst/latest/userguide/set-up-cli.html
- IAM authorization boundary: https://docs.aws.amazon.com/service-authorization/latest/reference/list_codecatalyst.html
- CodeCatalyst roles and effective permissions: https://docs.aws.amazon.com/codecatalyst/latest/userguide/ipa-roles.html
- Package-repository PAT use: https://docs.aws.amazon.com/codecatalyst/latest/userguide/packages-maven-curl.html
- CloudTrail behavior: https://docs.aws.amazon.com/codecatalyst/latest/userguide/ipa-logging-connections.html
- Per-space event logs: https://docs.aws.amazon.com/codecatalyst/latest/APIReference/API_ListEventLogs.html
- Identity-federated spaces: https://docs.aws.amazon.com/codecatalyst/latest/userguide/setting-up-topnode.html
