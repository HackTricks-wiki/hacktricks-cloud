# GKE / Container research checklist

## Completed documentation checks

- [x] Reconcile all technique sections with GKE Kubernetes audit-policy routing.
- [x] Distinguish streaming WebSocket `GET` telemetry from legacy POST/SPDY telemetry.
- [x] Correct TokenRequest to Admin Activity.
- [x] Correct node-pool create/update minimum IAM permissions to `container.clusters.update`.
- [x] Bound node-service-account pivots by Standard/Autopilot mode, metadata mode, OAuth scopes, IAM roles, scheduling, and admission.
- [x] Reconcile GKE long-running control-plane operation telemetry.
- [x] Reconcile Connect Gateway and GKE Hub audit methods/default visibility.
- [x] Correct Fleet predefined `ADMIN` semantics and custom-role prerequisites.
- [x] Add Config Sync downstream Kubernetes audit visibility.
- [x] Remove token/connect primitives that were incorrectly presented as automatic administrator escalation.
- [x] Add categorical Stealth, Potential Impact, minimum prerequisites, and expandable log tables to every retained technique.

## Safe future lab validation

- [ ] With a disposable Standard cluster, test `container.clusters.impersonate` against ordinary users/groups and protected `system:*` identities using a minimum custom IAM role.
- [ ] Capture `protoPayload.methodName`, authorization info, and `impersonatedUser` for impersonated read and write requests.
- [ ] Capture audit events for attach and port-forward using both current WebSocket and any supported legacy transport.
- [ ] Test `nodes/proxy` read endpoints and whether the kubelet `run` endpoint is exposed on current release channels.
- [ ] Test TokenRequest with: Google IAM identity plus `container.clusters.get`; native Kubernetes credential plus RBAC; and missing each prerequisite.
- [ ] Compare `CreateNodePool`/`UpdateNodePool` start and completion audit records and verify whether node recreation occurs for each metadata-mode transition.
- [ ] Validate `iam.serviceAccounts.actAs` enforcement on new cluster/new pool and its absence when only metadata mode changes on an existing pool.
- [ ] Capture Connect Gateway read, write, and stream audit methods plus downstream GKE Kubernetes audit records.
- [ ] Validate Fleet `ADMIN`, `EDIT`, `VIEW`, and an allowlisted custom ClusterRole on membership- and scope-level bindings.
- [ ] Capture Config Sync `Feature`/`MembershipFeature` Admin Activity and the reconciler's target-cluster Kubernetes audit identity.
- [ ] For Multi-Cloud, Edge, and on-prem products, verify token/connect access using a caller that authenticates successfully but has no in-cluster RBAC, confirming the authorization boundary.
- [ ] Preview lead: with minimum Kubernetes RBAC on `GCPAuthzExtension`/`GCPAuthzPolicy`, a same-namespace Service/Deployment, and an existing Gateway, test whether selected `Authorization` headers reach the callout, how timeout/error fail-open or fail-closed behavior works, and whether policy replacement can bypass an existing authorization control. Capture CRD writes, resulting Google Cloud resources, Gateway traffic logs, and cleanup behavior. Official source: <https://docs.cloud.google.com/kubernetes-engine/docs/how-to/configure-gke-service-extensions>.

For every future live test: use minimum custom roles, remain under the cost limit, export relevant audit records, and delete all clusters, pools, memberships, bindings, webhooks, workloads, and IAM grants immediately after validation.
