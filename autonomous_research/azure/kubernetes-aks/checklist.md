# Kubernetes / AKS — Candidate Attacks (not yet lab-fired)

Cost/risk note: a 1-node cluster's VM cost is likely near/over the $5/30min gate; auth mutations on a
shared cluster are risky. Fire only on a dedicated throwaway 1-node cluster in a short window, then delete.

- [ ] Live-fire **Run Command** with ONLY `runCommand`+`commandResults/read` (no kubeconfig, no network
      line-of-sight) to confirm it beats private-cluster / authorized-IP isolation; capture logs.
- [ ] Confirm `managedClusters/write` re-arm: set attacker group as `adminGroupObjectIDs`, flip
      disableLocalAccounts=false, obtain admin kubeconfig via listClusterAdminCredential.
- [ ] Test `trustedAccessRoleBindings/write` as durable MI-backed cluster access (persistence).
