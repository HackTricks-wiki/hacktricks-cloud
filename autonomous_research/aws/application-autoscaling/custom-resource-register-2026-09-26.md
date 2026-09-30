# Application Auto Scaling custom-resource registration review — 2026-09-26

## Decision

Do not publish `application-autoscaling:RegisterScalableTarget` with `service-namespace=custom-resource` as a generic PassRole, arbitrary AWS API, or SSRF technique. The documented integration is a fixed custom-scaling protocol over an Amazon API Gateway URL, and it uses the dedicated AWS-managed service-linked role rather than a caller-selected high-privilege role.

The narrower signed-request candidate is also closed. A follow-up with the exact AWS reference path shape reached Application Auto Scaling's caller-permission validation. A principal with only `RegisterScalableTarget` and first-use service-linked-role creation could not invoke the route directly and registration was rejected because it lacked the target API and CloudWatch permissions. AWS documents this as an intentional preflight: the service validates that the API caller already has the permissions it will use against the target service and CloudWatch. Registration therefore does not bridge a caller into the broader permissions of the service-linked role.

## Official protocol and role boundary

AWS documents the custom resource ID as the path to a custom resource **through Amazon API Gateway**. The official `aws/aws-auto-scaling-custom-resource` template defines only two SigV4-protected methods:

- `GET` reads the scaling state. Its response requires `actualCapacity`, `desiredCapacity`, `scalableTargetDimensionId`, `scalingStatus`, and `version`.
- `PATCH` requests a capacity change. Its JSON request body requires one numeric field, `desiredCapacity`, and the response uses the same state schema.

No operation name, target AWS service, arbitrary request body, arbitrary headers, or caller-selected HTTP method is part of this protocol. The documented resource ID is an API Gateway `execute-api.<region>.amazonaws.com` URL, not a general-purpose HTTP destination. Accordingly, the public contract supports only a fixed custom-scaling GET/PATCH exchange; it does not establish an arbitrary AWS API invocation or general network SSRF primitive.

For custom resources, registration automatically creates and uses:

```text
AWSServiceRoleForApplicationAutoScaling_CustomResource
```

The role trusts only `custom-resource.application-autoscaling.amazonaws.com`. Its immutable `AWSApplicationAutoScalingCustomResourcePolicy` grants only:

```text
execute-api:Invoke
cloudwatch:PutMetricAlarm
cloudwatch:DescribeAlarms
cloudwatch:DeleteAlarms
```

All four actions currently use `Resource: "*"`, but this is still not a bridge to unrelated AWS API permissions. The role can invoke API Gateway and maintain scaling alarms; it cannot assume roles, vend credentials, or call arbitrary AWS services.

The generic `RoleARN` member is misleading in this candidate scan. The RegisterScalableTarget API states that it is required for services without service-linked roles, while services that support service-linked roles use the service-linked role. AWS's IAM integration guide further states that Application Auto Scaling supports customer-managed service roles only for Amazon EMR. AWS separately notes that CloudFormation can put the applicable service-linked-role ARN in `RoleARN` even before the role exists; that is not permission to substitute an arbitrary role for a custom resource.

The documented caller-side path is therefore:

1. `application-autoscaling:RegisterScalableTarget` for the custom-resource tuple.
2. Caller-side permission for `execute-api:Invoke` on the required GET/PATCH route and `cloudwatch:PutMetricAlarm`, `cloudwatch:DescribeAlarms`, and `cloudwatch:DeleteAlarms`. Application Auto Scaling validates these target-service and CloudWatch permissions before accepting the scaling configuration.
3. On the first target in an account, `iam:CreateServiceLinkedRole` constrained to `custom-resource.application-autoscaling.amazonaws.com` and the exact service-linked-role ARN.
4. No caller-supplied execution-role permissions. If a client explicitly supplies the applicable service-linked-role ARN, the Service Authorization Reference lists `iam:PassRole` with `iam:PassedToService = application-autoscaling.amazonaws.com`; AWS's CLI example omits `RoleARN` and relies on automatic service-linked-role creation.

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

The endpoint contained only synthetic state. Its observability was deliberately limited to request shape and calling-principal metadata, without credential or authorization values. It received no invocation.

Three correctly shaped registration attempts were relevant:

1. A restricted caller with only `application-autoscaling:RegisterScalableTarget`, omitting `RoleARN`.
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

Because even the administrator received the same validation response with and without an explicit role, this run could not determine the runtime `iam:CreateServiceLinkedRole` / `iam:PassRole` ordering, whether a supplied non-service-linked role is ignored or rejected, or the eventual request-signing principal. The official IAM contract above remains the basis for excluding arbitrary-role execution. No scheduled action was created because there was no scalable target to trigger safely.

### CloudTrail

After normal Event History delivery latency, all three relevant calls appeared as CloudTrail management events with this sanitized shape:

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

The events separately attributed the restricted role and the administrator session. The failed explicit-role attempt also preserved the supplied role ARN in `requestParameters`, but there was no subsequent STS assumption or endpoint request. The API, Lambda, IAM, and log-group fixture operations remained ordinary account management activity.

## Exact-path follow-up — 2026-09-27

The first fixture used `/prod/scale`, whereas the AWS reference implementation uses `/prod/scalableTargetDimensions/<identifier>`. A syntax differential with the latter shape and a nonexistent API hostname passed namespace/dimension validation and failed later with `URL host cannot be resolved`. This also caused first-use creation of `AWSServiceRoleForApplicationAutoScaling_CustomResource`; the role was immediately deleted after the zero-target check.

A fresh disposable REST API then implemented the exact reference path with IAM-authorized GET and PATCH methods and a Lambda backend containing only synthetic scaling state. The restricted caller had exactly:

```text
application-autoscaling:RegisterScalableTarget
iam:CreateServiceLinkedRole
  iam:AWSServiceName = custom-resource.application-autoscaling.amazonaws.com
```

The caller's direct SigV4 GET returned HTTP 403. Its registration request reached the current custom resource integration but failed before target creation or endpoint invocation with:

```text
ValidationException: User is missing the following permissions:
cloudwatch:PutMetricAlarm, execute-api:Invoke:PATCH, execute-api:Invoke:GET,
cloudwatch:DeleteAlarms, cloudwatch:DescribeAlarms
```

This is the expected boundary described in AWS's permissions-validation documentation: Application Auto Scaling issues authorization probes for the target service and CloudWatch on behalf of the API caller and rejects registration if those permissions are absent. The caller must therefore already possess the API invocation rights that the candidate hoped to obtain through the service-linked role.

Two preparatory fixture iterations were discarded before interpreting any AWS result: one temporary Lambda package used an invalid hidden module name, and one local preflight attempted to import an uninstalled Python `botocore` module. Their cleanup traps ran successfully. The final run used curl's native SigV4 implementation for the direct-access control.

## Cleanup and independent zero-residue verification

All REST APIs (including stages, deployments, resources, and methods), Lambda functions, dedicated log groups, S3 canary buckets/objects, IAM roles, and inline policies were deleted. No scalable target, scaling policy, scheduled action, or alarm was created. Service-linked roles created by the follow-up syntax and exact-route checks were deleted after confirming that no target referenced them.

Independent post-cleanup inventories confirmed:

- zero custom-resource scalable targets matching the fixture;
- zero matching scheduled actions, scaling policies, and CloudWatch alarms;
- the custom-resource service-linked role was absent after deletion completed;
- zero fixture-prefixed API Gateway APIs;
- zero fixture-prefixed Lambda functions;
- zero fixture-prefixed IAM roles;
- zero fixture-prefixed CloudWatch Logs log groups; and
- zero local fixture-prefix files.

## Revisit gate

The candidate is closed under the current contract. Revisit only if AWS removes caller-side target permission validation, permits a non-API-Gateway destination or caller-selected role, or exposes a new custom-resource method/body that creates a materially different primitive. Do not probe third-party endpoints, internal addresses, or metadata services.

## Official sources

- <https://docs.aws.amazon.com/autoscaling/application/userguide/services-that-can-integrate-custom.html>
- <https://docs.aws.amazon.com/autoscaling/application/APIReference/API_RegisterScalableTarget.html>
- <https://docs.aws.amazon.com/autoscaling/application/userguide/security_iam_service-with-iam.html>
- <https://docs.aws.amazon.com/autoscaling/application/userguide/security_iam_permission_validation.html>
- <https://docs.aws.amazon.com/autoscaling/application/userguide/application-auto-scaling-service-linked-roles.html>
- <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSApplicationAutoScalingCustomResourcePolicy.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_application-autoscaling.html>
- <https://github.com/aws/aws-auto-scaling-custom-resource>
- <https://github.com/aws/aws-auto-scaling-custom-resource/blob/master/cloudformation/templates/custom-resource-stack.yaml>
