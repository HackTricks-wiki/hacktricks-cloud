# Access Context Manager — tested

Access Context Manager / VPC-SC. Covered (policies.setIamPolicy hidden IAM surface, CEL bypass, vpcAccessibleServices widening, dry-run drop anti-forensics, accessLevels/servicePerimeters.replaceAll).

## 2026-09-29 — Workforce extended Looker sessions

- Mapped the Preview `GcpUserAccessBinding.scopedAccessSettings` path. One organization-wide all-workforce-pools binding can append `restricted_project` scopes whose active session settings raise eligible Looker core workforce sessions from 12 hours to at most 90 days with no idle timeout. It does not affect other applications or other Looker projects.
- Retained it as bounded service/session persistence and extended the existing binding privesc technique. Required ACM authority is `.create`/`.update` in `gcpAccessAdmin`; provider changes separately need Workforce Pool Admin. OIDC needs authorization-code flow plus `offline_access` or SCIM; SAML needs SCIM. The fixed 24-hour attribute-staleness check preserves deprovisioning.
- Current CLI supports scoped-setting replacement and `--append`; append is limited to session-only settings. Writes are the existing `Create/UpdateGcpUserAccessBinding` Admin Activity methods at organization scope. Reads are Data Access and off by default.
- The lab has no visible organization/workforce fixture, so no API or binding was mutated. This was an official-contract, CLI-help, and predefined-role review with no cleanup obligation.

## Role facts — VERIFIED
- `accesscontextmanager.policies.setIamPolicy` is in `policyAdmin` only (NOT `policyEditor`) — confirmed via `gcloud iam roles describe`.
- `gcpAccessAdmin` holds only `gcpUserAccessBindings.*`.
- `roles/resourcemanager.organizationAdmin` contains no `accesscontextmanager.*` permissions. The live predefined-role catalog confirms organization-level basic Editor/Owner do contain the ACM write permissions, but Google's access-control documentation says permissions granted on folders or projects have no effect on access policies. Valid authority comes from the organization or a direct IAM binding on the target access policy; `gcpUserAccessBindings` are organization resources.
- Google's current audit-method table confirms every documented ACM mutation is Admin Activity and always logged. LRO writes usually generate start and completion entries; IAM/config reads are Data Access and disabled by default. All seven book techniques now have an expandable event table and a categorical stealth rating.

## Standing UNVERIFIED candidate
- Full-teardown chain `replaceAll`×2 (accessLevels + servicePerimeters) → `policies.delete` — a 3-call complete VPC-SC/access-level dismantle. **Unverified, omitted** — needs a live disposable access policy.
