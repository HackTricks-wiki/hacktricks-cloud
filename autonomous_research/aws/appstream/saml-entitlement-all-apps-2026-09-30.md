# AppStream SAML entitlement all-applications escalation — 2026-09-30

## Outcome

Verified that `appstream:CreateEntitlement` scoped to one exact stack ARN can create an
`AppVisibility=ALL` entitlement matching an attacker-selected supported SAML PrincipalTag value.
Also verified that exact-stack `appstream:UpdateEntitlement` alone can replace an existing
`ASSOCIATED`/selected-app entitlement with the same all-applications grant.

Expected AWS functionality only. No AWS defect or private report.

## Security model and boundaries

- Entitlements apply only to SAML-federated application catalogs. User-pool/API streaming users
  already receive all stack applications, while Desktop stream view and Dynamic Application
  Framework apps ignore this entitlement plane.
- The assertion carries a full attribute URI such as
  `https://aws.amazon.com/SAML/Attributes/PrincipalTag:groups`; the AppStream API stores the short
  key `groups`.
- Supported keys are roles, department, organization, groups, title, costCenter, and userType.
- Effective access is the union of all matching entitlements. `ALL` includes applications added to
  the stack in the future.
- The attacker still needs a valid signed SAML assertion containing the chosen tag value and the
  existing SAML federation role/trust/relay configuration. Entitlement mutation cannot forge that
  identity or add `sts:TagSession` to the federation trust.
- Entitlements filter the application catalog; AWS states that they do not stop a user already in
  a Desktop-view session from launching an installed application directly.

## Live exact-resource proofs

Account `228478051196`, Region `us-east-1`. No fleet or IdP fixture was required for control-plane
authorization tests.

Create branch:

- an administrator created an otherwise empty disposable stack;
- a restricted session with only `appstream:CreateEntitlement` on its exact ARN created
  `ht-entitlement-all-20260930`, matching `groups=ht-controlled`, with `AppVisibility=ALL`;
- `DescribeEntitlements` and the same operation under a policy naming another stack were denied;
  and
- the stored response contained the expected stack, name, description, ALL visibility, and
  attribute.

Update branch:

- an administrator created a baseline `ASSOCIATED` entitlement matching `groups=approved`;
- a restricted session with only exact-stack `appstream:UpdateEntitlement` changed it to
  `AppVisibility=ALL` and `groups=ht-controlled` without Describe or application permissions; and
- a different-stack policy was denied.

An initial attempt passed the full PrincipalTag URI as the API `Name` and was rejected with
`InvalidParameterValueException`. `Name=groups` is the correct API representation, as confirmed by
the live call and the CloudFormation property reference.

No SAML assertion or application launch was performed because the account had no disposable
third-party IdP fixture. AWS's official entitlement documentation establishes the matching and
catalog semantics; the least-privilege mutation itself was live-verified.

## Telemetry

`CreateEntitlement` and `UpdateEntitlement` are default AppStream management writes. Successful
events retained stack/name, description, `AppVisibility`, and complete attribute name/value lists
in the request; the response returned the complete resulting entitlement with created/modified
times. The invalid full-URI attempt retained that URI but appeared as generic `UnknownError` in
CloudTrail. Wrong-stack IAM denials had null request fields and top-level `AccessDenied`.

Detection should correlate an `ASSOCIATED`-to-`ALL` transition or unfamiliar attribute match with
subsequent SAML federation/session usage.

## Cleanup evidence

Both disposable entitlements were deleted before their stacks. The update fixture exposed a short
deletion-propagation race: the first immediate `DeleteStack` attempt left the stack present. A
bounded cleanup retry waited for the entitlement to disappear and then removed the exact stack.
Independent final inventories returned zero matching entitlements and stacks. No fleet,
application, app block, SAML provider, IAM role, session, URL, S3 object, network resource, or
compute fixture was created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateEntitlement.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateEntitlement.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_Entitlement.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/application-entitlements-saml.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-appstream-entitlement-attribute.html
