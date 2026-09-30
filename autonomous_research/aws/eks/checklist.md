# EKS — checklist

- [ ] `eks:UpdateAddon --service-account-role-arn` + PassRole — repoint a managed add-on's IRSA role.
      Verify authz gate + whether the add-on then runs as the chosen role.
- [ ] `eks:UpdateCapability --role-arn` (new capability construct) + PassRole — repoint gate.
- [ ] `eks:AssociateEncryptionConfig` — envelope-encryption KMS key add (persistence/defense-evasion?).
- [ ] disable-session-tags end-to-end: confirm on a real cluster that stripping tags actually bypasses a
      trust-policy ABAC condition keyed on kubernetes-namespace (compute-gated: needs a cluster + pod).
