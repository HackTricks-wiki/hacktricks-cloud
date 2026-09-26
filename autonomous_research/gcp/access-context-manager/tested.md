# Access Context Manager — tested

Access Context Manager / VPC-SC. Covered (policies.setIamPolicy hidden IAM surface, CEL bypass,
vpcAccessibleServices widening, dry-run drop anti-forensics, accessLevels/servicePerimeters.replaceAll).

## Role facts — VERIFIED
- `accesscontextmanager.policies.setIamPolicy` is in `policyAdmin` only (NOT `policyEditor`) — confirmed
  via `gcloud iam roles describe`.
- `gcpAccessAdmin` holds only `gcpUserAccessBindings.*`.
- `roles/resourcemanager.organizationAdmin` contains no `accesscontextmanager.*` permissions. The
  live predefined-role catalog confirms organization-level basic Editor/Owner do contain the ACM
  write permissions, but Google's access-control documentation says permissions granted on folders
  or projects have no effect on access policies. Valid authority comes from the organization or a
  direct IAM binding on the target access policy; `gcpUserAccessBindings` are organization resources.
- Google's current audit-method table confirms every documented ACM mutation is Admin Activity and
  always logged. LRO writes usually generate start and completion entries; IAM/config reads are Data
  Access and disabled by default. All seven book techniques now have an expandable event table and a
  categorical stealth rating.

## Standing UNVERIFIED candidate
- Full-teardown chain `replaceAll`×2 (accessLevels + servicePerimeters) → `policies.delete` — a 3-call
  complete VPC-SC/access-level dismantle. **Unverified, omitted** — needs a live disposable access policy.
