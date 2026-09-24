# Kubernetes / AKS — Tests Done

Wiki: `az-kubernetes-privesc.md`, post-exploitation, persistence, unauth `az-aks-kubernetes-unauth`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Run Command (`runCommand`+`commandResults/read`) in-cluster exec w/o kubeconfig/network | those actions | DOC-ONLY |
| 2 | `managedClusters/write` re-arm (disableLocalAccounts=false + attacker aadProfile.adminGroupObjectIDs → system:masters) | that action | DOC-ONLY |
| 3 | Node/kubelet IMDS MI theft → cluster → Azure pivot | node access | DOC-ONLY |
| 4 | `namespaces/listUserCredential`, `rotateClusterCertificates`, agentPools/write | those actions | DOC-ONLY |
| 5 | `trustedAccessRoleBindings/write` MI standing access (persistence) | that action | DOC-ONLY |
| 6 | Flux GitOps self-heal, `extensions/write` (persistence) | those actions | DOC-ONLY |
| 7 | ARO `listCredentials` | that action | DOC-ONLY |
| 8 | Public API-server `/version` + anon RBAC + workload-SSRF→IMDS (unauth) | none | DOC-ONLY (unauth page) |

Cost note: AKS clusters incur node VM cost + risky auth mutation on shared infra → NOT live-fired.
