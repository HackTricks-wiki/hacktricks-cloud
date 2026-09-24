# finspace-kx — open idea (cost-blocked)

- [ ] **q-code injection privesc** — `finspace:UpdateKxClusterCodeConfiguration` pushes attacker
  kdb+ q-code onto an existing managed-kdb cluster; if q can invoke arbitrary AWS APIs as the
  cluster's `executionRole` (not just kdb/S3 ops) it's a clean confused-deputy exec primitive.
  BLOCKED: >$5/30min, not onboarded in lab, arbitrary-AWS-call capability unverifiable here.
  Revisit if budget/onboarding allows a minimal cluster with a 1-hour teardown. Otherwise it stays
  folded into the generic ml-dataaccess-passrole catalog as a reasoned exclusion.
