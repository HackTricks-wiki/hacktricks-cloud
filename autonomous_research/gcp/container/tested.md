# GKE / Container privilege-escalation audit

## 2026-09-28 documentation validation

Scope: static validation of `gcp-container-privesc.md` against current Google Cloud and upstream Kubernetes primary documentation. No cloud resources were created or changed in this pass.

Confirmed/corrected findings:

- GKE Kubernetes audit routing is verb based: `create`, `update`, `patch`, `delete`, and `deletecollection` are Admin Activity; most reads are Data Access and disabled by default. Secret/configuration-sensitive audit records use reduced metadata levels.
- `kubectl exec` is explicitly Admin Activity and GKE adds `command.gke.io/command` with command arguments.
- WebSocket `GET` for attach/port-forward is Data Access, while legacy SPDY `POST` is Admin Activity. Proxy calls likewise follow the actual verb.
- TokenRequest is `create` on `serviceaccounts/token`, so it is Admin Activity rather than a quiet Data Access read.
- Node-pool create and update REST methods require `container.clusters.update`; `container.nodePools.create` and `container.nodePools.update` are not the authorization permissions for those operations.
- Changing an existing Standard node pool to `GCE_METADATA` does not require `iam.serviceAccounts.actAs` when the node service account is unchanged. The resulting token is bounded by both VM OAuth scopes and the service account's IAM roles.
- GKE control-plane create/update operations are Admin Activity long-running operations and commonly produce start/completion records.
- Connect Gateway has no separately documented `GenerateCredentials` audit method. Used kubeconfigs produce `GetResource` Data Access for reads and Admin Activity for mutation/stream methods; the target cluster can also audit the forwarded request.
- Fleet predefined `ADMIN` is not Kubernetes `cluster-admin`; it is the Fleet admin access level (edit plus RBAC permissions). A custom role only applies when allowed/configured.
- Config Sync feature/member mutations are GKE Hub Admin Activity. On GKE targets, Config Sync object writes are also visible as Kubernetes Admin Activity.
- GKE Multi-Cloud `generateAccessToken`, Distributed Cloud Edge token generation, and GKE on-prem `connect` authenticate or transport a caller; none independently grants Kubernetes administrator authorization. The three former standalone privilege-escalation headings were folded into a non-technique warning.
- Direct `container.pods.update` cannot mutate an existing Pod's service account, containers, volumes, environment, command, or arguments. Controller Pod-template update or Pod create is required for those workload-injection paths.
- Mutating admission webhook effects are not inherently invisible: target object writes remain Admin Activity and mutation/patch annotations are available at sufficient Kubernetes audit levels.

Not live-tested in this pass:

- Product/version-specific acceptance of impersonating `system:masters` with `container.clusters.impersonate`.
- Availability of a kubelet `run` endpoint behind `nodes/proxy` on current GKE versions.
- Exact node-roll behavior for each `workloadMetadataConfig` transition.
- Fleet custom-role allowlisting and propagation timing across mixed GKE/non-GKE memberships.

## Preview lead triage: GKE Gateway authorization extensions

The Preview `networking.gke.io/v1` `GCPAuthzExtension` plus `GCPAuthzPolicy` surface is a useful post-exploitation/recon lead, but it is not yet a distinct GKE privilege-escalation technique for this page. A caller already able to create/update the CRDs, deploy/control the referenced same-namespace HTTP/2 Service, and target an existing Gateway can receive selected request headers (potentially including `Authorization`) and influence allow/deny decisions. That can expose application credentials, bypass an application authorization gate if callout and policy behavior permit it, or cause denial of service. It does not by itself expand Kubernetes RBAC or GCP IAM.

Documented constraints: Preview; GKE 1.33+ and Gateway API; Gateway, policy, extension, and referenced Service are same-namespace; one `CUSTOM` policy per Gateway; the authorization extension receives request headers only, not request body or response data. Keep it in the research ledger until a minimum-permission lab test shows a meaningful authorization boundary crossing; then place it under GKE post-exploitation rather than this privilege-escalation page. Official source: <https://docs.cloud.google.com/kubernetes-engine/docs/how-to/configure-gke-service-extensions>.
