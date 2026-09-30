# AWS RTB Fabric — managed endpoint and control-plane audit (2026-09-30)

## Scope and inventory

- RTB Fabric was absent from the public HackTricks Cloud corpus at the start of this pass.
- Signed `ListRequesterGateways` and `ListResponderGateways` calls succeeded in `us-east-1` and `eu-west-1`; both inventories were empty. Other probed supported Regions were denied by the training account's organization policy.
- The current service exposes requester/responder gateways, same-fabric links, inbound/outbound external links and mutable link module flows.
- AWS documents all RTB Fabric control-plane APIs as CloudTrail management events. Transaction/application telemetry is separately sampling-dependent.

## High-value expected techniques

### Responder managed-endpoint replacement

`rtbfabric:UpdateResponderGateway` is resource-scoped to a responder gateway and can replace either:

- Auto Scaling group names, discovery role and health-check settings; or
- EKS cluster API URI/CA, cluster name, Kubernetes `Endpoints` namespace/name and discovery role.

The update requires the current port/protocol even if they are unchanged. A replacement can redirect future OpenRTB traffic to controlled or compromised backend compute, but does not itself grant AWS IAM permissions or return credentials. The current Service Authorization Reference lists exact-responder `UpdateResponderGateway` with no dependent `iam:PassRole` action. The effective boundary still includes a correctly tagged/service-trusting managed-endpoint role, backend reachability and endpoint health/discovery.

### Link module-flow sabotage

`rtbfabric:UpdateLinkModuleFlow` is resource-scoped to a link. Modules can create no-bid results, set pass-through percentage, enforce a TPS rate limit, filter OpenRTB attributes, emit no-bids and add headers. A malicious replacement can suppress all or selected requests, throttle throughput or influence downstream behavior. This is application integrity/availability impact, not IAM privilege escalation.

### Conditional external-link exfiltration

`rtbfabric:CreateOutboundExternalLink` is resource-scoped to a requester gateway and accepts a public HTTP/HTTPS endpoint. Creation alone does not make the requester application select the new link, so this is only a staged exfiltration/traffic-redirection primitive until a separate selection/configuration path sends traffic through it.

## Live managed-EKS endpoint experiment

### Safety design

- Region: `us-east-1`; existing default VPC/subnet/default security group only.
- Synthetic endpoint: one disposable API Gateway HTTP API and Lambda.
- The Lambda recorded only method/path/user-agent, authorization presence and scheme, Kubernetes bearer prefix, `x-k8s-aws-id`, and SHA-256 of authorization. It never logged raw authorization material.
- Managed endpoint role trusted `rtbfabric.amazonaws.com` and `rtbfabric-endpoints.amazonaws.com`, was tagged `RTBFabricManagedEndpoint=true`, and had **zero IAM policies and zero EKS RBAC**.
- No EKS cluster, real bid traffic, requester gateway, link or application workload existed.

### Results

1. A first create attempt while the service-linked role was absent caused AWS to create `AWSServiceRoleForRTBFabric`, then returned `AccessDeniedException: Unable to assume the service linked role`. No gateway was created. Waiting for role propagation was required before retry.
2. The next `CreateResponderGateway` accepted the synthetic EKS configuration and returned `PENDING_CREATION`.
3. The responder reached `ACTIVE` at monitoring check 49. The only request in the capture log was the harness's own unauthenticated `/probe`; RTB Fabric made no HTTP request to the supplied URI and exposed no authorization metadata.
4. `UpdateResponderGateway` with the same synthetic EKS configuration succeeded while active and returned `ACTIVE` immediately. The service again made no callback.
5. A preliminary update with a hyphenated description failed validation because descriptions match `[A-Za-z0-9 ]+`; retrying with an alphanumeric/space description succeeded.

### Observed CloudTrail serialization

- `CreateResponderGateway`, `UpdateResponderGateway` and `DeleteResponderGateway` were management events with `readOnly:false`; `GetResponderGateway` was a management event with `readOnly:true`.
- Successful and failed create/update events retained their request fields. For the successful EKS update, CloudTrail exposed the cluster API URI, cluster name, namespace, `Endpoints` resource name and role ARN; it masked the base64 CA chain as `***`.
- The write-event response contained gateway ID/status, while read response elements were omitted. `resources` was null, so detections should inspect `eventSource`, `eventName` and `requestParameters.gatewayId` rather than requiring a populated resource array.
- The 15-second lifecycle polling produced a large number of default `GetResponderGateway` management events, making aggressive polling conspicuous.

### Security conclusion

The tested creation and update control-plane paths store an arbitrary-looking EKS API URI but do not contact it by themselves. The hypothesized immediate EKS bearer-token leak/SSRF was **negative** under these conditions. A traffic-triggered discovery test would require a separate requester gateway/link/application fixture and remains deferred until cleanup reliability is understood. Do not represent the accepted URI alone as credential theft or SSRF.

No private AWS security report was created.

## Cleanup and operational observations

- Responder deletion remained `PENDING_DELETION` for 77 15-second checks (roughly nineteen minutes), then the gateway became absent.
- Immediately afterward, independent inventory found zero requester gateways, responder gateways, `RTBFabricManaged=true` ENIs, test Lambdas, HTTP APIs, log groups and `ht-rtb-capture-*` IAM roles.
- The test-created `AWSServiceRoleForRTBFabric` remained after every dependent resource disappeared. Repeated supported `DeleteServiceLinkedRole` tasks returned `FAILED` with reason `Cannot delete the role due to internal errors` and an empty `RoleUsageList`. Direct policy detach/role delete correctly returned `UnmodifiableEntity` because AWS protects service-linked roles.
- The role has only `RTBFabricServiceRolePolicy`, no inline policies or tags, and its last-use timestamp corresponds to the gateway deletion path. Slow supported deletion retries remain active. This is an operational cleanup defect/caveat without demonstrated security impact; do not create more RTB fixtures until the role is absent.
- Continuation 126 retried the supported deletion path with task `40ede7ee-5daf-4d5a-949f-1f30368d3e2f`. It again reached `FAILED` with `Cannot delete the role due to internal errors` and an empty `RoleUsageList`; the role's last-use timestamp remained `2026-09-30T14:09:02Z`.

## Next tests

1. Continue supported service-linked-role deletion until independent `GetRole` returns not found.
2. If cleanup becomes reliable, use a separate bounded requester/link fixture to determine whether real linked traffic triggers EKS endpoint discovery and whether the supplied URI is bound to the named cluster. Never log raw tokens.
3. Verify with a restricted caller that runtime behavior matches the authorization table's lack of a dependent `iam:PassRole` action for `UpdateResponderGateway`.
4. Live-test exact-link `UpdateLinkModuleFlow` on a synthetic link, preserve/restore the original ordered flow and inspect CloudTrail request serialization.
5. Live-test `CreateOutboundExternalLink` authorization without sending application traffic, then delete it before gateway cleanup.
