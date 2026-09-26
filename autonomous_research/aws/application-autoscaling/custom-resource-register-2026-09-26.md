# Application Auto Scaling custom-resource registration review — 2026-09-26

## Decision

Do not publish `application-autoscaling:RegisterScalableTarget` with
`service-namespace=custom-resource` as a generic PassRole, arbitrary AWS API, or SSRF technique. The
documented integration is a fixed custom-scaling protocol over an Amazon API Gateway URL, and it uses
the dedicated AWS-managed service-linked role rather than a caller-selected high-privilege role.

There is a narrower candidate worth retaining for a future compatible lab: registration might cause
the low-privilege service-linked role to make SigV4-signed GET/PATCH requests to a caller-controlled
API Gateway route. That could matter only where a target API explicitly accepts that role. It was not
live-verifiable in the authorized `us-east-1` account because the service rejected the documented
custom-resource tuple before creating a target, role, or request. This is therefore a reasoned
exclusion/defer, not a verified offensive primitive.

## Official protocol and role boundary

AWS documents the custom resource ID as the path to a custom resource **through Amazon API Gateway**.
The official `aws/aws-auto-scaling-custom-resource` template defines only two SigV4-protected methods:

- `GET` reads the scaling state. Its response requires `actualCapacity`, `desiredCapacity`,
  `scalableTargetDimensionId`, `scalingStatus`, and `version`.
- `PATCH` requests a capacity change. Its JSON request body requires one numeric field,
  `desiredCapacity`, and the response uses the same state schema.

No operation name, target AWS service, arbitrary request body, arbitrary headers, or caller-selected
HTTP method is part of this protocol. The documented resource ID is an API Gateway
`execute-api.<region>.amazonaws.com` URL, not a general-purpose HTTP destination. Accordingly, the
public contract supports only a fixed custom-scaling GET/PATCH exchange; it does not establish an
arbitrary AWS API invocation or general network SSRF primitive.

For custom resources, registration automatically creates and uses:

```text
AWSServiceRoleForApplicationAutoScaling_CustomResource
```

The role trusts only `custom-resource.application-autoscaling.amazonaws.com`. Its immutable
`AWSApplicationAutoScalingCustomResourcePolicy` grants only:

```text
execute-api:Invoke
cloudwatch:PutMetricAlarm
cloudwatch:DescribeAlarms
cloudwatch:DeleteAlarms
```

All four actions currently use `Resource: "*"`, but this is still not a bridge to unrelated AWS API
permissions. The role can invoke API Gateway and maintain scaling alarms; it cannot assume roles,
vend credentials, or call arbitrary AWS services.

The generic `RoleARN` member is misleading in this candidate scan. The RegisterScalableTarget API
states that it is required for services without service-linked roles, while services that support
service-linked roles use the service-linked role. AWS's IAM integration guide further states that
Application Auto Scaling supports customer-managed service roles only for Amazon EMR. AWS separately
notes that CloudFormation can put the applicable service-linked-role ARN in `RoleARN` even before the
role exists; that is not permission to substitute an arbitrary role for a custom resource.

The documented caller-side path is therefore:

1. `application-autoscaling:RegisterScalableTarget` for the custom-resource tuple.
2. On the first target in an account, `iam:CreateServiceLinkedRole` constrained to
   `custom-resource.application-autoscaling.amazonaws.com` and the exact service-linked-role ARN.
3. No caller-supplied execution-role permissions. If a client explicitly supplies the applicable
   service-linked-role ARN, the Service Authorization Reference lists `iam:PassRole` with
   `iam:PassedToService = application-autoscaling.amazonaws.com`; AWS's CLI example omits `RoleARN`
   and relies on automatic service-linked-role creation.

## Sanitized live check

Authorized lab, `us-east-1`:

### Preflight

- `DescribeScalableTargets` for `custom-resource` returned no targets.
- `AWSServiceRoleForApplicationAutoScaling_CustomResource` did not exist.
- No fixture-prefixed API Gateway API, Lambda function, IAM role, or log group existed.

### Disposable fixture

A unique test-only prefix was used for:

- one regional API Gateway REST API with IAM-authorized GET and PATCH methods;
- one Lambda backend and its one-day-retention log group;
- one least-privilege Lambda execution role;
- one restricted registration caller role; and
- one disposable candidate passed role limited to invoking the exact test API route.

The endpoint contained only synthetic state. Its observability was deliberately limited to request
shape and calling-principal metadata, without credential or authorization values. It received no
invocation.

Three correctly shaped registration attempts were relevant:

1. A restricted caller with only `application-autoscaling:RegisterScalableTarget`, omitting
   `RoleARN`.
2. The administrator, omitting `RoleARN`.
3. The administrator, explicitly supplying the disposable candidate role ARN.

Each used the documented namespace and dimension:

```text
service namespace: custom-resource
scalable dimension: custom-resource:ResourceType:Property
resource ID: owned API Gateway HTTPS route
```

All three failed before target creation or endpoint invocation with the exact service response:

```text
ValidationException: Unsupported service namespace, resource type or scalable dimension
```

Because even the administrator received the same validation response with and without an explicit
role, this run could not determine the runtime `iam:CreateServiceLinkedRole` / `iam:PassRole` ordering,
whether a supplied non-service-linked role is ignored or rejected, or the eventual request-signing
principal. The official IAM contract above remains the basis for excluding arbitrary-role execution.
No scheduled action was created because there was no scalable target to trigger safely.

### CloudTrail

After normal Event History delivery latency, all three relevant calls appeared as CloudTrail
management events with this sanitized shape:

```text
eventSource: autoscaling.amazonaws.com
eventName: RegisterScalableTarget
eventCategory: Management
managementEvent: true
readOnly: false
requestParameters.serviceNamespace: custom-resource
requestParameters.scalableDimension: custom-resource:ResourceType:Property
requestParameters.resourceId: <owned API Gateway HTTPS route>
requestParameters.roleARN: absent, absent, then <disposable candidate role ARN>
errorCode: ValidationException
errorMessage: Unsupported service namespace, resource type or scalable dimension
```

The events separately attributed the restricted role and the administrator session. The failed
explicit-role attempt also preserved the supplied role ARN in `requestParameters`, but there was no
subsequent STS assumption or endpoint request. The API, Lambda, IAM, and log-group fixture operations
remained ordinary account management activity.

## Cleanup and independent zero-residue verification

The REST API (including its stage, deployment, resources, and methods), Lambda function, dedicated log
group, three IAM roles, and their inline policies were deleted. No scalable target, scaling policy,
scheduled action, alarm, or custom-resource service-linked role had been created.

Independent post-cleanup inventories confirmed:

- zero custom-resource scalable targets matching the fixture;
- zero matching scheduled actions, scaling policies, and CloudWatch alarms;
- the custom-resource service-linked role remained absent;
- zero fixture-prefixed API Gateway APIs;
- zero fixture-prefixed Lambda functions;
- zero fixture-prefixed IAM roles;
- zero fixture-prefixed CloudWatch Logs log groups; and
- zero local fixture-prefix files.

## Revisit gate

Revisit only in an account and explicitly authorized Region where the documented custom-resource tuple
successfully registers. Use an owned API Gateway endpoint with synthetic state, omit `RoleARN` first,
and test these boundaries independently:

- caller with RegisterScalableTarget but without first-use CreateServiceLinkedRole;
- caller with the exact service-linked-role creation permission;
- explicit service-linked-role ARN with and without exact `iam:PassRole`;
- explicit ordinary role ARN, expected from the IAM documentation to be rejected or unused;
- actual GET/PATCH signer identity and exact body shape; and
- one bounded scheduled action followed by deregistration and service-linked-role deletion.

Do not probe third-party endpoints, internal addresses, or metadata services. Promote to the public book
only if the service accepts a controlled route and demonstrates a privilege boundary materially broader
than the fixed low-privilege protocol documented here.

## Official sources

- <https://docs.aws.amazon.com/autoscaling/application/userguide/services-that-can-integrate-custom.html>
- <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html>
- <https://docs.aws.amazon.com/autoscaling/application/userguide/security_iam_service-with-iam.html>
- <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-service-linked-roles.html>
- <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSApplicationAutoScalingCustomResourcePolicy.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_application-autoscaling.html>
- <https://github.com/aws/aws-auto-scaling-custom-resource>
- <https://github.com/aws/aws-auto-scaling-custom-resource/blob/master/cloudformation/templates/custom-resource-stack.yaml>
