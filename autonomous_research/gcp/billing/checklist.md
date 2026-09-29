# Cloud Billing research checklist

## Verified MCP/enumeration surface — 2026-09-29

- [x] Inventory all 29 remote MCP tools and their read/write annotations.
- [x] Separate public catalog, private negotiated pricing, project association, account hierarchy,
      and Billing IAM permission boundaries.
- [x] Map wrapper, Resource Manager, Billing Data Access/Admin Activity, and unaudited public-catalog
      telemetry.
- [x] Confirm no MCP tool updates a project's billing assignment; direct REST/gcloud remains a
      separate two-resource authorization boundary.
- [ ] In a dedicated reseller billing test account, exercise subaccount create/delete lifecycle and
      a reversible account move without touching production billing or payment instruments.
- [ ] In a disposable billing account, compare exact `tool.name` conditions for private pricing,
      IAM reads, and `set_iam_policy`; preserve and immediately restore the original etag/version-3
      policy.

## Verified from current official documentation — 2026-09-28

- [x] Billing-account IAM is separate from project IAM and can inherit organization bindings.
- [x] `billing.accounts.setIamPolicy` is sufficient for a direct complete-policy replacement;
      additive gcloud IAM helpers first need `billing.accounts.getIamPolicy`.
- [x] `billing.accounts.setIamPolicy` custom-role support level is `SUPPORTED`, and billing custom
      roles must be created at organization scope before being applied to a billing account.
- [x] `roles/billing.admin`, `roles/billing.user`, `roles/billing.costsManager`,
      `roles/billing.projectManager`, `roles/billing.creator`, and `roles/billing.viewer` current GA
      permission sets were inspected read-only.
- [x] Billing association requires target-account `billing.resourceAssociations.create` and
      project-side `resourcemanager.projects.createBillingAssignment`; a billing-account binding
      does not satisfy the project-side check.
- [x] Payment-profile exception and payment-method removal boundary for
      `billing.accounts.updatePaymentInfo`.
- [x] Exact Cloud Billing audit methods, categories, default visibility, non-LRO status, and
      billing-account log query scope.
- [x] Rejected recon, destructive-only, defense-evasion, post-exploitation, persistence, ordinary
      resource-creation, and pure cost-abuse claims as separate privilege-escalation headings.
- [x] Independently re-open current official access-control, payment, association, role and audit
      references after the first-pass rewrite.

## Safe future validation leads

- [ ] In a disposable billing lab with explicit authorization, compare a raw etag-preserving
      `setIamPolicy` call under a write-only custom role with the additive helper's denied
      `GetIamPolicy`; immediately restore the original policy.
- [ ] Capture `SetIamPolicy` and `AssignResourceToBillingAccount` billing-account log resource names,
      authorizationInfo resources, policy redaction, and project/billing-account event placement;
      immediately remove the binding and unlink the disposable project.
- [ ] With a disposable payments profile and no real payment instrument, determine the exact
      user-visible activity/notification evidence for permitted payment-info edits. Do not infer a
      Cloud Audit Logs method until Google publishes or a safe test captures it.
- [ ] Recheck role drift and Cloud Billing audit method names after API or FinOps feature updates.
