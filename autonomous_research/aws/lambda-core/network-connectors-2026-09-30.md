# AWS Lambda Core network connectors — 2026-09-30

## Scope

- Audited the 2026 `lambda-core` service model in AWS CLI 2.37.6, the Lambda Core API reference and current Service Authorization Reference.
- Lambda Core currently manages VPC-egress network connectors used by Lambda MicroVM images/runtimes. The API namespace is `lambda-core`; IAM actions remain under `lambda:` and CloudTrail uses `lambda.amazonaws.com`.
- A connector stores subnet IDs, security-group IDs, IPv4/dual-stack mode, associated compute resource types and an operator role. Create/update asynchronously provision managed ENIs.

## Live authorization and behavior

Account `228478051196`, `us-east-1`; default VPC only, no MicroVM and no application traffic.

1. Initial `ListNetworkConnectors` returned an empty inventory.
2. Created one operator role trusted by `lambda.amazonaws.com` for `sts:AssumeRole` / `sts:TagSession` and attached the AWS-managed `AWSLambdaNetworkConnectorOperatorPolicy`.
3. Created connector `nc-cae52984-5671-4ee9-b3b4-daf274f63291` with one default-VPC subnet/security group. It reached `ACTIVE` after roughly three and a half minutes.
4. A restricted session with only exact-connector `lambda:UpdateNetworkConnector` was denied by caller-side validation on `ec2:DescribeSecurityGroups`; no configuration changed.
5. A second session had exact-connector `lambda:UpdateNetworkConnector` plus only `ec2:DescribeSecurityGroups`, `ec2:DescribeSubnets`, and `ec2:DescribeVpcs` on `*`. It omitted `OperatorRole`, had no `iam:PassRole`, and successfully replaced the subnet while retaining the stored operator role.
6. The connector remained `ACTIVE`, reported `LastUpdateStatus: InProgress`, then reached `Successful` after several minutes with the replacement subnet as its active configuration.

This supports a conditional post-exploitation technique: connector writers can move MicroVM VPC egress into another subnet/security boundary allowed by the existing operator role without re-passing that role. The action alone does not run or control a MicroVM or guarantee useful private reachability.

## Telemetry

- `CreateNetworkConnector` and `UpdateNetworkConnector` were default management writes under `lambda.amazonaws.com`, with `resources: []`.
- Requests and responses retained connector ID/ARN, subnet IDs, security-group IDs, protocol, compute type and operator-role ARN. The restricted successful update response showed `ACTIVE` plus `LastUpdateStatus: InProgress`.
- The initial caller-side EC2 denial appeared as `UpdateNetworkConnector` with `errorCode: AccessDenied` and the complete nested EC2 authorization message, but null request parameters. Deletion retained the connector ID in the request and the full last configuration/operator role with `DELETING` in the response.
- `GetNetworkConnector` polling generated default management reads; Event History omitted their response bodies.
- The operator role produced EC2 `CreateNetworkInterface` events invoked by `network-connectors.lambda.amazonaws.com`. One dry-run validation event preceded the actual create. The create recorded connector tags, VPC, subnet, SG, managed-operator marker, ENI/private IP and assumed operator-role ARN.

## Cleanup

- Deleted the exact connector, observed `DELETING`, confirmed `ResourceNotFoundException`, then independently confirmed `ListNetworkConnectors` is empty.
- Confirmed zero ENIs carrying the exact `aws:lambda:networkConnectorId` tag.
- Detached the AWS-managed operator policy, deleted the exact operator role and confirmed `NoSuchEntity`.
- No Lambda MicroVM image/runtime, function, application workload, custom VPC/subnet/security group, route, endpoint, NAT, database or traffic target was created.

## Follow-up hypotheses

- Verify whether an already-running MicroVM immediately adopts a successful connector update or retains its original ENI path until restart/resume. Do not overstate live-workload redirection until traffic is observed.
- Test cross-VPC updates and connector reuse across images with controlled private canaries.
- Test update/delete behavior while an attached MicroVM is suspended or running, including rollback on failed ENI provisioning.
- Evaluate `lambda:PassNetworkConnector` scoping and whether a connector identifier can be confused across accounts/Regions in `RunMicrovm` or image updates.

Expected functionality only; no private AWS vulnerability report.
