# Access Context Manager — tested

Access Context Manager / VPC-SC. Covered (policies.setIamPolicy hidden IAM surface, CEL bypass,
vpcAccessibleServices widening, dry-run drop anti-forensics, accessLevels/servicePerimeters.replaceAll).

## Role facts — VERIFIED
- `accesscontextmanager.policies.setIamPolicy` is in `policyAdmin` only (NOT `policyEditor`) — confirmed
  via `gcloud iam roles describe`.
- `gcpAccessAdmin` holds only `gcpUserAccessBindings.*`.

## Standing UNVERIFIED candidate
- Full-teardown chain `replaceAll`×2 (accessLevels + servicePerimeters) → `policies.delete` — a 3-call
  complete VPC-SC/access-level dismantle. **Unverified, omitted** — needs a live disposable access policy.
