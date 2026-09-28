# Config Controller research checklist

## Completed

- [x] Compare current `roles/krmapihosting.admin/editor/viewer` permissions with the old self-grant claim.
- [x] Inspect local GA `get-credentials` and `get-config-connector-identity` command source.
- [x] Verify cluster-mode and namespaced-mode Config Connector IAM identity boundaries.
- [x] Verify `IAMServiceAccountKey` automatic Secret behavior and suppression annotation.
- [x] Correct Kubernetes audit visibility and downstream caller attribution.
- [x] Remove destructive-only and duplicate post-exploitation headings.

## Safe future checks

- [ ] On a disposable Config Controller, capture exact custom-resource Kubernetes audit method names
  for `IAMPolicyMember` and `IAMServiceAccountKey`; the public GKE documentation guarantees the
  `k8s.io` Admin Activity class but does not publish every CRD method string.
- [ ] Test the narrowest lifecycle custom role needed for `IAMServiceAccountKey` reconciliation
  (`create` alone versus create/get/list/delete) and record controller retry behavior.
- [ ] Compare Secret Data Access logging defaults on newly created Standard and Autopilot-backed
  Config Controller instances.
- [ ] Test Policy Controller constraints that prevent KCC IAM and key resources from being admitted.

Any future test must use a disposable instance, a non-sensitive test service account, immediate key
revocation/deletion, and full custom-resource and instance cleanup.
