# Generic GCP permission patterns — research ledger

## 2026-09-28 — no-garbage consolidation

- Reduced four vague headings to two actionable patterns: resource `setIamPolicy` self-grant and `iam.serviceAccounts.actAs` combined with a real code-executing resource write.
- Removed `.create`/`.update` and `*ServiceAccount*` as standalone techniques. Their names do not establish identity attachment, useful execution, a public method or a privilege transition.
- Bounded resource IAM to the exact attachment point, grantable roles, policy version/etag, conditions, Deny and principal-access-boundary enforcement. A catalog permission without a usable public IAM method is not sufficient evidence.
- Corrected the generic `actAs` telemetry claim. IAM documents a separate `iam.serviceAccounts.actAs` Admin Activity record when an attachment check is evaluated; the resource write and later downstream calls remain separate signals.
- Used current official IAM attachment, legacy-enforcement, permission, hierarchy and audit references. No cloud API, IAM policy, workload or service configuration was read or changed.

## 2026-09-28 — reciprocal review

- Revalidated both retained patterns against the current IAM attachment, cross-project service account and audit-log examples. `iam.serviceAccounts.actAs` emits its own always-on `iam.googleapis.com` Admin Activity record when the attachment check is evaluated; it is not only an authorization detail inside the destination resource write.
- Confirmed that generic `setIamPolicy` impact must remain bounded to the actual attachment point and grantable roles. The page appropriately avoids promising a public IAM method or Cloud Audit integration from a permission name alone.
- No content correction was required. No IAM policy, service account, workload or cloud resource was read or changed.
