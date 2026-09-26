# EKS — tested

## VERIFIED (authz, two-sided) — `eks:UpdatePodIdentityAssociation` + `iam:PassRole` repoint
- **Idea:** repoint an EXISTING Pod Identity association (by associationId) onto a chosen role
  (`--role-arn`); plus two dimensions the documented CreatePodIdentityAssociation technique omits:
  `--target-role-arn` (Pod Identity ROLE CHAINING, incl. cross-account) and `--disable-session-tags`
  (strip kubernetes-namespace/service-account/eks-cluster-arn session tags => bypass ABAC guardrails on
  the target role). Works when Create is denied but Update allowed; stealthier (rides a trusted assoc).
- **Result (2026-09-25, acct 228478051196, us-east-1):**
  - NEG (no PassRole) & NEG2 (PassRole wrong arn): `AccessDeniedException ... not authorized to perform:
    iam:PassRole on resource: .../ht-eks-target because no identity-based policy allows the iam:PassRole action`.
  - POS (PassRole allowed on target): `ResourceNotFoundException: No cluster found for name: ht-bogus-cluster`
    => IAM gate passed; PassRole evaluated BEFORE the cluster lookup.
  - Target role trusts pods.eks.amazonaws.com with sts:AssumeRole + sts:TagSession. Roles ht-eks-target/
    ht-eks-att torn down (NoSuchEntity).
- **Min perms:** `eks:UpdatePodIdentityAssociation`, `iam:PassRole` (on a pods.eks-trusting role),
  `iam:GetRole` (same undocumented requirement as the create path). + ability to schedule/await a pod
  under the association's SA to redeem it.
- **Status:** SHIPPED — aws-eks-privesc/README.md new section, ref [11], PR #413.

## Pre-existing (documented)
- CreateAccessEntry/AssociateAccessPolicy/UpdateAccessEntry (cluster-admin), CreatePodIdentityAssociation
  +PassRole+GetRole, UpdateClusterConfig (public endpoint), CreateNodegroup/CreateFargateProfile+PassRole.
