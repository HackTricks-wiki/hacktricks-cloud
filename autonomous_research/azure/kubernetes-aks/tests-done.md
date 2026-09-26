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
| 9 | `rotate-certs` revocation check — does it actually kill a leaked `--admin` kubeconfig? | `managedClusters/rotateClusterCertificates/action` (defender side) | **WORKS/CONFIRMED** — lab-verified 2026-09-25; rotation DOES revoke the leaked client cert |

**Cost note (CORRECTED 2026-09-25):** a **1-node `Standard_B2s`, `--tier free`** AKS cluster is well
under the $5/30min gate (node ≈ $0.04/hr, free control plane) and provisions in ~4-5 min — AKS **is**
live-fireable in a short dedicated-throwaway window, contrary to the earlier "NOT live-fired" note.

**Lab record (test, 2026-09-25 — rotate-certs revocation):** RG `htrc-aksrot`, cluster `htrcaks29629`
(1× B2s, free tier). `az aks get-credentials --admin` → `kubectl auth whoami` = `masterclient` /
`[system:masters system:authenticated]`, `get nodes` OK (client-cert serial `D787…BF62`, 2-yr validity).
Ran `az aks rotate-certs --yes` (~341s / 5.7 min). **After rotation:** the old kubeconfig failed — but the
naive re-test gives a *client-side* `x509: certificate signed by unknown authority` (kubeconfig still pins
the OLD cluster CA vs the server's new-CA cert), which is NOT proof of revocation. The definitive test —
`kubectl --insecure-skip-tls-verify` with the OLD client cert — returned **`Unauthorized`** from the API
server, i.e. the client credential is genuinely revoked. A fresh `--admin` kubeconfig worked and carried a
**different** serial (`8B89…FA75`). So the wiki's remediation claim HOLDS (unlike the Cosmos resource-token
case). Added a lab-verified NOTE to `az-aks-kubernetes-unauth.md` incl. the client-vs-server-cert nuance and
the reminder that `aadProfile.adminGroupObjectIDs` / Trusted-Access MI paths survive rotation.
**Teardown:** `az group delete htrc-aksrot`; background monitor also verifies the `MC_` node RG is removed.
