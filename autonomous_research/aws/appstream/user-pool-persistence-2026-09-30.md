# AppStream user-pool identity and association persistence — 2026-09-30

## Outcome

Verified that `appstream:CreateUser` on `Resource: "*"` plus exact-stack
`appstream:BatchAssociateUserStack` creates an enabled regional user-pool identity with durable
stack access. Also verified that `appstream:EnableUser` alone restores a disabled identity while
its stack assignment remains intact.

Expected AWS functionality only. No AWS defect or private report.

## Security model

- A real foothold uses an attacker-controlled deliverable email address. The welcome message
  contains the permanent regional login portal and a temporary password valid for seven days; the
  user chooses a permanent password on first login.
- `MessageAction=SUPPRESS` prevents the welcome email. That safely creates the control-plane record
  but is not an immediate usable credential.
- `SendEmailNotification=false` on the association suppresses only the assignment notice, not the
  welcome email/password flow.
- New users are enabled by default. Disabling them retains stack assignments, so a principal with
  `EnableUser` and control of the existing password can restore access with one action.
- User-pool assignments are incompatible with stacks whose fleet is Active Directory joined.
- The identity is regional and service-local; it is not an IAM user and does not automatically
  grant a fleet's machine role.

## Live minimum-permission proof

Account `228478051196`, Region `us-east-1`. Tests used two disposable stacks and reserved `.invalid`
email addresses. `MessageAction=SUPPRESS` and `SendEmailNotification=false` ensured that no message
could be delivered and no external party was contacted.

Fresh-user branch:

- a restricted STS session with only `CreateUser` on `*` and `BatchAssociateUserStack` on the exact
  stack created an enabled `USERPOOL` user in `FORCE_CHANGE_PASSWORD` and assigned it;
- `DescribeUsers` was denied, and a policy authorizing a different stack ARN was denied;
- the first immediate batch association returned HTTP 200 with `USER_NAME_NOT_FOUND` inside
  `errors`; retrying after roughly two seconds succeeded with an empty errors array; and
- no fleet, session, password delivery, or login was needed for the control-plane proof.

Resurrection branch:

- an administrator created and assigned a second suppressed fixture, then disabled it;
- `DescribeUserStackAssociations` still returned the same association while the user was disabled;
- a restricted session with only `appstream:EnableUser` on `*` restored `Enabled:true` without
  Describe permission; and
- the association remained unchanged after re-enabling.

The email/password login behavior and seven-day temporary credential are established by AWS's
official user-pool documentation; they were deliberately not exercised with an external mailbox.

## Telemetry

- `CreateUser` is a default management write. CloudTrail replaced user name/email and first/last
  name with `HIDDEN_DUE_TO_SECURITY_REASONS`, while retaining `authenticationType` and
  `messageAction`.
- `BatchAssociateUserStack` retained stack name and `sendEmailNotification`, redacted the user
  name, and returned `errors: []` on success. The propagation failure also had no top-level
  `errorCode`; its member error appeared only under `responseElements.errors`.
- Wrong-stack IAM denial had null request fields and a normal `AccessDenied` top-level error.
- `EnableUser` retained `authenticationType: USERPOOL` while replacing `userName` with
  `HIDDEN_DUE_TO_SECURITY_REASONS`; the successful management event had no response body.
- Portal activity is operational/session traffic; optional daily usage reports provide delayed
  user/stack/fleet/client attribution.

## Cleanup evidence

Each assignment was explicitly disassociated before its user and stack were deleted. Independent
final inventories found zero matching user-pool users and stacks. No email was sent, and no fleet,
session, URL, IAM role, S3 object, application, network interface, or compute resource was created.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateUser.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_BatchAssociateUserStack.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_EnableUser.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/user-pool.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/user-pool-admin-create.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/user-pool-admin-assigning.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/user-pool-admin-unassigning.html
