# finspace (Managed kdb) — tested/assessed 2026-09-25
- CreateKxCluster: executionRole -> q-code execution + S3/kx access AS role. PassRole candidate.
- CreateKxUser/UpdateKxUser: iamRole -> binds a kdb user to an IAM role; connecting as the user vends the role. Distinct role-binding privesc/persistence.
- Ordering probe (admin, no infra): CreateKxUser against fake env -> ResourceNotFoundException (env validated BEFORE iam:PassRole) => a NEG PassRole probe needs a REAL KxEnvironment, which is slow (dedicated tenancy, ~1h) + costly (kdb clusters bill hourly). => DOC-GROUNDED per cost/time exception.
- Shipped: row added to ml-dataaccess-passrole table (CreateKxCluster + CreateKxUser note). No dedicated page (niche + doc-grounded).
