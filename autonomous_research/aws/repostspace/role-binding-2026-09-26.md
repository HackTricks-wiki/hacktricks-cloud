# AWS re:Post Private `CreateSpace` / `UpdateSpace(roleArn)` review

## Verdict — real but constrained support delegation; reasoned exclusion

The optional `roleArn` is not a general PassRole execution surface. AWS re:Post Private assumes the
role only for its built-in AWS Support-case workflow. The documented and AWS-managed permission set is
limited to creating a case, adding attachments or communications, describing cases and communications,
and resolving a case. The API has no field that selects an arbitrary AWS operation, returns temporary
credentials, or exports the private re:Post knowledge base through the role.

This is still a meaningful delegation boundary in an existing deployment: a re:Post Private user can
cause AWS Support API calls without possessing an AWS account or IAM identity. However, application
authorization is an additional prerequisite. AWS documents the **Support requester** role as permitting
a user to convert only a question that they posted, after it has been unanswered for at least 12 hours.
Support responses and the user's replies are private to that user unless the user deliberately publishes
the correspondence back to the private thread.

Consequently, changing `roleArn` alone gives an IAM caller no usable application session, no Support
requester role, and no arbitrary role execution. A practical abuse path would additionally require
control of an existing private re:Post identity that has Support requester permission, or separate
permissions to administer/invite users and assign re:Post roles. It could then create or alter Support
cases by design and send selected thread content to AWS Support. It does not establish a documented way
to browse unrelated account Support cases, expose content to the public internet, or invoke unrelated
permissions attached to an overprivileged role.

This does not merit a new public privesc page: the path is narrow, needs an existing application identity
and entitlement, was not end-to-end testable in the lab, and the service is already closed to new
customers with final shutdown scheduled for June 30, 2027.

## Current availability

AWS currently states that re:Post Private is no longer available to new customers. Existing customers
can continue until June 30, 2027; after that date the service and all unexported data are permanently
unavailable/deleted. The residual API and CLI models therefore matter only to existing customers.

The documented legacy prerequisites are:

- Enterprise Support or Enterprise On-Ramp Support.
- IAM Identity Center configured in the same supported Region.
- An existing same-account role trusted by re:Post Private for Support integration.
- An existing private re:Post user assigned Support requester permission for the question-to-case flow.

Supported Regions are `us-east-1`, `us-west-2`, `eu-central-1`, `eu-west-1`, `ap-southeast-1`,
`ap-southeast-2`, and `ca-central-1`.

## Caller authorization and resource boundary

The current Service Authorization Reference maps both operations to `iam:PassRole` with the fixed
condition value `iam:PassedToService = repostspace.amazonaws.com`:

- `CreateSpace` has no resource type and must use `Resource: "*"`. `repostspace:TagResource` is an
  additional dependent action only when tags are supplied.
- `UpdateSpace` supports an exact space ARN:
  `arn:aws:repostspace:<region>:<account-id>:space/<space-id>` and the
  `aws:ResourceTag/<key>` condition family.
- `roleArn` is optional in both APIs, so PassRole is relevant only when the request sets or replaces it.
- IAM only permits PassRole to a service in the same AWS account. This field is therefore not a direct
  cross-account role-binding primitive.

Minimum role-binding policy shape for an existing space:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "repostspace:UpdateSpace",
      "Resource": "arn:aws:repostspace:<region>:<account-id>:space/<space-id>"
    },
    {
      "Effect": "Allow",
      "Action": "iam:PassRole",
      "Resource": "arn:aws:iam::<account-id>:role/<support-integration-role>",
      "Condition": {
        "StringEquals": {
          "iam:PassedToService": "repostspace.amazonaws.com"
        }
      }
    }
  ]
}
```

For creation, replace the first statement with `repostspace:CreateSpace` on `*`; add
`repostspace:TagResource` if the create request includes tags. The first space also causes AWS to create
`AWSServiceRoleForrePostPrivate`; AWS says administrators must allow service-linked-role creation, so
`iam:CreateServiceLinkedRole` for `repostspace.amazonaws.com` is an operational first-space dependency
even though it is not listed as a dependent action in the re:Post authorization table.

## Passed-role trust and permissions

The exact documented trust policy is:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "repostspace.amazonaws.com"},
    "Action": ["sts:AssumeRole", "sts:SetSourceIdentity"]
  }]
}
```

`arn:aws:iam::aws:policy/AWSRepostSpaceSupportOperationsPolicy` currently grants on `Resource: "*"`:

- `support:AddAttachmentsToSet`
- `support:AddCommunicationToCase`
- `support:CreateCase`
- `support:DescribeCases`
- `support:DescribeCommunications`
- `support:ResolveCase`

The wildcard reflects the AWS Support APIs' account-level resource model; it is not proof that the
private application exposes an arbitrary case browser. The documented end-user workflow remains tied to
the requester's own question/case. An overprivileged customer role is poor hygiene, but no documented
re:Post input makes the service invoke arbitrary non-Support actions from that role.

This customer-selected role is distinct from `AWSServiceRoleForrePostPrivate`. The service-linked role
only trusts `repostspace.amazonaws.com` and permits `cloudwatch:PutMetricData` in the
`AWS/rePostPrivate` and `AWS/Usage` namespaces.

## Data and external-content boundary

- Private re:Post content is not returned by `CreateSpace`, `UpdateSpace`, or `GetSpace`; `GetSpace`
  returns configuration such as domains, role ARN, application identifiers, users/roles, tier, and
  aggregate size/count fields.
- A Support requester can populate a new Support case from the title, summary, comments/answers, tags,
  and topics of their own question, with an opportunity to remove confidential information first.
- AWS Support responses and requester replies are initially visible only to the requester. The requester
  can later publish correspondence to the private thread. This is internal-space disclosure, not public
  or cross-account publication.
- The role does not grant access to the private knowledge corpus. Offboarding/export of all questions,
  answers, discussions, articles, and metadata is a separate TAM-mediated S3 process, not a roleArn API
  capability.

## Cost, onboarding, and cleanup

Historical pricing offers six months of Free Tier and then Standard at USD 12 per user per month. New
customers can no longer enroll. Creation takes approximately 30 minutes, requires Identity Center, and
creates an AWS-generated domain, an Identity Center application relationship, and a service-linked role.
Custom subdomains require AWS approval.

`DeleteSpace` exists, but deletion is destructive and takes approximately 30 minutes; AWS says all space
configuration and content becomes unrecoverable. A Support case created during an end-to-end test is a
separate AWS Support record: it can be resolved, but there is no delete-case action. This makes a real
Support workflow a poor disposable fixture even for an existing customer.

No paid space or onboarding state was created for this review.

## Live inventory and bounded negative probe

Authorized account `228478051196`, profile `ht-admin`, 2026-09-26:

- `ListSpaces` returned empty in the two Regions allowed by the current SCP: `us-east-1` and
  `eu-west-1`. The other five supported Regions were explicitly denied by organization SCP
  `p-oat9rg2i`, so their service inventory could not be asserted.
- IAM Identity Center had no instance visible in `us-east-1`; `eu-west-1` exposed the active
  organization instance owned by the management account.
- No IAM role trusted `repostspace.amazonaws.com`.
- No identity had `AWSRepostSpaceSupportOperationsPolicy` attached.
- `AWSServiceRoleForrePostPrivate` did not exist.
- `GetSpace` on synthetic ID `htnonexistent000000000000` returned
  `ResourceNotFoundException: Space ID given was not found`.
- A single `UpdateSpace` using that already-proven-absent ID and a syntactically valid pre-existing role
  ARN returned the same `ResourceNotFoundException`. The role did not trust re:Post Private and was not
  modified. A subsequent `ListSpaces` still returned empty.

The negative update demonstrates a clean nonexistent-resource boundary, not successful PassRole
enforcement or role assumption. There is no space, role/policy attachment, Identity Center application,
service-linked role, Support case, billing subscription, or cleanup residue from this review.

## Logging

AWS documents all re:Post Private API calls as CloudTrail management events under
`repostspace.amazonaws.com`, including `CreateSpace` and `UpdateSpace`. Its published `CreateSpace`
example records the `roleArn` in `requestParameters`, with `readOnly=false`, `eventType=AwsApiCall`, and
`managementEvent=true`.

The bounded failed update was observed with `eventSource=repostspace.amazonaws.com`,
`eventName=UpdateSpace`, `eventType=AwsApiCall`, `eventCategory=Management`, `managementEvent=true`, and
`readOnly=false`. Its request parameters contained both the synthetic space ID and the full supplied
role ARN. CloudTrail recorded `ResourceNotFoundException` and the service message in response elements.

The built-in Support workflow produces events under `support.amazonaws.com`. AWS specifically documents
`CreateCase`, `AddCommunicationToCase`, and `ResolveCase`; its `ResolveCase` example shows the passed role
as the assumed-role session and the re:Post user identifier in `sessionContext.sourceIdentity`. Alerting
should therefore correlate a space role change with later Support events from that role/source identity.
Successful role assumption and Support events were not tested because no space exists.

## Completed checks

- [x] Inspect AWS CLI 2.34.45 API shapes for create, update, get, and delete.
- [x] Confirm CreateSpace wildcard and UpdateSpace exact-resource authorization.
- [x] Confirm both conditional PassRole dependencies and same-account boundary.
- [x] Confirm trust policy, managed Support policy, and separate CloudWatch service-linked role.
- [x] Trace Support requester prerequisites and question/case visibility.
- [x] Check current availability, pricing, supported Regions, and destructive cleanup behavior.
- [x] Inventory spaces, Identity Center, IAM trust, policy attachments, and service-linked role.
- [x] Run one bounded nonexistent-space update and re-inventory for zero residue.
- [x] Capture the failed update's exact CloudTrail event classification and request parameters.

## Revisit only for an existing test-owned customer space

- [ ] Capture and restore the original `customerRoleArn` byte-for-byte.
- [ ] Use an isolated caller with only exact-space `UpdateSpace` plus exact-role PassRole.
- [ ] Confirm PassRole denial and trust-policy denial independently.
- [ ] Use a synthetic Identity Center requester and non-sensitive 12-hour-old unanswered question.
- [ ] Verify that the role performs only the six documented Support operations and cannot invoke an
  unrelated permission intentionally added to the test role.
- [ ] Verify whether the requester can see any unrelated Support case or communication; current docs do
  not establish such exposure.
- [ ] Resolve the synthetic case, restore the original space role, remove the synthetic identity/content,
  and accept that the resolved Support case and CloudTrail history are non-deletable audit residue.

## Official sources

- <https://aws.amazon.com/repost-private/>
- <https://docs.aws.amazon.com/repostprivate/latest/APIReference/API_CreateSpace.html>
- <https://docs.aws.amazon.com/repostprivate/latest/APIReference/API_UpdateSpace.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_repostspace.html>
- <https://docs.aws.amazon.com/repostprivate/latest/caguide/repost-manage-permissions.html>
- <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSRepostSpaceSupportOperationsPolicy.html>
- <https://docs.aws.amazon.com/repostprivate/latest/caguide/using-service-linked-roles.html>
- <https://docs.aws.amazon.com/repostprivate/latest/caguide/assign-user-role.html>
- <https://docs.aws.amazon.com/repostprivate/latest/userguide/convert-question-support-case.html>
- <https://docs.aws.amazon.com/repostprivate/latest/caguide/logging-using-cloudtrail.html>
- <https://docs.aws.amazon.com/repostprivate/latest/caguide/delete-repost.html>
- <https://docs.aws.amazon.com/repostprivate/latest/caguide/quotas.html>
- <https://aws.amazon.com/repost-private/pricing/>
- <https://docs.aws.amazon.com/repostprivate/latest/userguide/repost-private-end-of-support.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_passrole.html>
