# Lake Formation attack-surface audit — 2026-09-26

## Scope

Reviewed current Lake Formation coverage and AWS primary documentation for data-lake settings,
named and LF-TBAC grants, saved LF-Tag expressions, registered-location roles, hybrid access,
credential vending, cross-account RAM/resource links, and CloudTrail boundaries. Live validation
used the authorized `hacktricks-training` account in `us-east-1`; every AWS CLI invocation set
`AWS_DEFAULT_OUTPUT=json`, `AWS_DEFAULT_REGION`, `AWS_REGION`, and an empty pager.

The earlier broad post-exploitation review remains in
`autonomous_research/aws/lakeformation/post-exploitation-audit-2026-09-26.md`. This ledger records
the additional attack-specific findings and live checks requested in the follow-up audit.

## High-value expected techniques retained

### Saved LF-Tag expression mutation

AWS explicitly documents that `UpdateLFTagExpression` immediately changes the boundaries of all
existing `LFTagPolicy` grants that reference the saved expression. This creates a useful
grant-amplification path without a new `GrantPermissions` call.

Required boundaries:

- IAM `lakeformation:UpdateLFTagExpression` on `*` because Lake Formation exposes no IAM resource
  ARN.
- Data lake administrator, saved-expression creator, or LF `ALTER`/`SUPER` on the expression.
- `GRANT_WITH_LF_TAG_EXPRESSION` on every key/value in the replacement expression.
- An existing named-expression grant and matching tagged resources; IAM/query/S3/KMS gates remain.

`CreateLFTagExpression` by itself is only setup. The saved expression matters offensively after a
grant references it. The useful persistence scope is every current and future resource matched by
those referencing grants.

### Registration-role delegation and `WithPrivilegedAccess`

Live validation established the following exact behavior:

| Test | Result |
| --- | --- |
| `RegisterResource --with-privileged-access` from the authorized admin role | Succeeded and produced `DATA_LOCATION_ACCESS` with grant option for the caller role. |
| Restricted caller with only `lakeformation:RegisterResourceWithPrivilegedAccess` plus `iam:PassRole`/`iam:GetRole` | Denied for missing `lakeformation:RegisterResource`. |
| Restricted non-data-lake-admin caller with both `lakeformation:RegisterResource` and `lakeformation:RegisterResourceWithPrivilegedAccess` plus role-scoped `iam:PassRole`/`iam:GetRole` | Registration succeeded. |

Thus the privileged flag requires **both** Lake Formation IAM actions and atomically grants the
caller role grantable `DATA_LOCATION_ACCESS`; data lake administrator membership is not required
for that grant. The custom registration role must trust `lakeformation.amazonaws.com` and carry
the relevant S3/KMS rights. This remains a bounded confused-deputy path: the caller needs catalog
creation/control, table permissions, `lakeformation:GetDataAccess`, and query/output permissions to
turn the location grant into bytes. It does not vend an arbitrary reusable role session.

Plain `RegisterResource` omits the automatic grant. `UpdateResource` can replace the vending role
for a custom-role registration, but service-linked-role registrations cannot be updated in place.

### Hybrid opt-out downgrade

AWS documents that `DeleteLakeFormationOptIn` stops LF enforcement for the selected
principal/resource pair and returns access control to IAM and Glue. A non-LF-admin probe using an
IAM administrator session returned `AccessDeniedException: Insufficient Lake Formation
permission(s) on Catalog`, confirming that the IAM API permission alone is insufficient. The path
is useful only when the target pair is already opted in and an IAM/Glue/S3 compatibility path
remains; it grants no new data-plane right by itself.

## Existing paths rechecked

- `PutDataLakeSettings` remains the highest-level regional escalation but replaces the whole
  settings document. The managed `AWSLakeFormationDataAdmin` policy explicitly denies it.
- `GrantPermissions`/`BatchGrantPermissions` requires IAM API authority plus LF administrator or
  matching grant-option authority. `GRANT_WITH_LF_TAG_EXPRESSION` is a Lake Formation permission,
  not a separate `GrantPermissionsWithLFTagExpression` API.
- Cross-account named/LF-TBAC grants still depend on producer Glue/RAM prerequisites, consumer
  acceptance/delegation, and resource links for Athena/Redshift Spectrum. A resource link only
  grants `DESCRIBE`/`DROP` on the link; it does not grant access to the target or producer S3 data.
- `GetDataAccess` and public temporary-credential APIs remain bounded by table LF permissions,
  registered role/prefix, external-engine or full-table account settings, session tags where
  applicable, and KMS/query rights.
- Data-cell filter mutation was not promoted: creating or broadening a filter requires table
  `SELECT` with grant option, which generally already conveys the underlying full-table selection
  authority and is not a useful independent escalation.

## Account-state blocker

The regional settings contain two stale data lake administrators whose IAM roles no longer exist:

- `arn:aws:iam::228478051196:role/ht-dzmar-2781914038`
- `arn:aws:iam::228478051196:role/ht-dzprov-2781914038`

An attempt to preserve the full settings and append the authorized test administrator was rejected
with `InvalidInputException` because those existing principals are invalid. Removing them would be
a persistent account-wide mutation, and the invalid original document could not then be restored,
so no settings, LF-Tag, saved-expression, database, table, grant, or opt-in mutation was performed.
The saved-expression result therefore rests on explicit AWS documentation rather than a live
fixture.

## CloudTrail conclusions

- Lake Formation calls are management events. Watch `UpdateLFTagExpression`,
  `DeleteLakeFormationOptIn`, `RegisterResource`, `UpdateResource`, and `DeregisterResource`.
- A saved-expression edit expands all referencing grants without new `GrantPermissions`/RAM events.
- `WithPrivilegedAccess` adds the location grant within `RegisterResource`; there is no separate
  grant event, so defenders should inspect `withPrivilegedAccess` and reconcile LF permissions.
- Credential vending (`GetDataAccess` and `GetTemporary*Credentials`) is a management event. S3
  object reads are data events and are absent unless object-level data-event logging is enabled.

## Cleanup verification

Every live registration fixture used a new empty S3 bucket, two disposable IAM roles at most, and a
custom registration role policy. Each registered location was deregistered before its bucket and
roles were deleted. Final account inventory showed:

- no registered resource containing `htx-lf-reg-`;
- no bucket beginning `htx-lf-reg-`;
- no IAM role beginning `htx-lf-data-` or `htx-lf-caller-`;
- no pre-existing LF settings or grants changed.

## Unexpected-flaw disposition

No AWS malfunction or authorization bypass was found. `WithPrivilegedAccess` is security-sensitive
but explicitly documented and guarded by its dedicated IAM action in addition to
`RegisterResource`. No private vulnerability report was created.
