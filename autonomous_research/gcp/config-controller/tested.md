# Config Controller — documentation audit

## 2026-09-28 — privilege-escalation and post-exploitation review

Documentation, predefined-role inspection, and local Google Cloud CLI source/help inspection only. No Config Controller instance, GKE cluster, Kubernetes object, IAM policy, service-account key, API, or other cloud state was read or changed.

### Retained privilege-escalation boundaries

1. **Kubernetes RBAC over KCC custom resources.** A KCC object is reconciled as the Google service account configured in the applicable `ConfigConnectorContext` or namespace mode. Escalation is bounded by that identity's actual IAM permissions. Google documents `roles/owner` only as a non-production convenience; it is not a guaranteed service grant.
2. **`IAMServiceAccountKey` plus Secret read.** KCC can create a user-managed service-account key and, by default, automatically import the private key into a same-name Kubernetes Secret. The caller needs RBAC to create the custom resource and read the Secret, while the configured KCC identity needs service-account-key creation permission on the target. Organization policy can block it. Current upstream KCC source stores the decoded credentials file under Secret data key `key.json`; it is not the IAM API response field name `privateKeyData`.

### Retained post-exploitation boundary

- **Kubernetes Secret read.** Kept as the only distinct post-exploitation H3. It can expose operator- supplied Cloud SQL passwords, Secret Manager payload inputs, Config Sync Git credentials, TLS keys, and KCC-generated service-account keys that actually exist in readable namespaces. It does not make every Google Cloud Secret Manager payload visible.

### Removed or rejected claims

- **`krmapihosting.krmApiHosts.setIamPolicy` to project takeover:** rejected as a false standalone boundary. `roles/krmapihosting.admin` contains only `krmapihosting.*` and resource-manager discovery; it does not include `container.clusters.get` or Kubernetes CRD-write authorization. Local gcloud source confirms `get-credentials` calls GKE `GetCluster` for `krmapihost-<name>`. An instance IAM self-grant therefore does not itself provide access to the backing cluster or KCC identity.
- **Fixed `gcp-sa-yakima` attribution:** removed. Current setup reads the identity from `ConfigConnectorContext.spec.googleServiceAccount`; downstream logs are attributed to that configured service account.
- **Arbitrary GCP reads through KRM:** rejected as written. Config Connector reconciles resource configuration; generic bucket/dataset creation does not proxy object or row reads. Minting a KCC SA key is already the explicit privilege-escalation technique.
- **Mass mutation/deletion and `krmApiHosts.delete`:** removed from post-exploitation as destructive impact/denial of service with no sensitive-information or foothold result.
- Generic CNRM inventory was folded into enumeration rather than retained as post-exploitation.

### Telemetry corrections

- Kubernetes API writes are GKE Kubernetes Admin Activity Cloud Audit Logs under service `k8s.io`, not unlogged in-cluster actions.
- Secret `get/list` and GKE `GetCluster` are Data Access and off by default.
- Downstream IAM/resource changes are logged as the configured Config Connector identity, while the preceding Kubernetes audit event records the cluster caller.
- `google.iam.admin.v1.CreateServiceAccountKey` is non-LRO Admin Activity and always on.

### Identity and CLI findings

- Local gcloud `get-credentials` constructs the backing cluster name as `krmapihost-<instance>` and invokes the GKE v1 GetCluster API before persisting kubeconfig data.
- Local gcloud `get-config-connector-identity` obtains the identity from `ConfigConnectorContext.spec.googleServiceAccount` in namespace `config-control`; it is not obtained from the `krmApiHost` resource IAM policy.
- `IAMPolicyMember` is additive rather than authoritative, so a project binding reconciliation needs the configured identity to read and set the target allow policy, not only to call `setIamPolicy`.
