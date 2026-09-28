# Cloud Billing research tested

## 2026-09-28 privilege-escalation documentation audit

This pass used current official Google Cloud documentation, local gcloud help/source, and read-only
inspection of GA predefined roles. It made no cloud-resource, IAM, API, payment, or billing changes.

### Retained primitive

- `billing.accounts.setIamPolicy` can turn a policy-write-only custom-role delegation into
  `roles/billing.admin` on the target billing account. The additive gcloud helper requires both
  `getIamPolicy` and `setIamPolicy`; a direct complete-policy replacement has only the write
  permission as its API authorization minimum.

### Material corrections and boundaries

- Reduced the page from recon, destructive, defense-evasion, post-exploitation, and cost-abuse
  headings to one genuine privilege-escalation primitive.
- Bounded billing-account IAM from organization/project IAM. A `roles/billing.admin` binding on a
  billing account does not grant its embedded Resource Manager permissions on linked projects.
- Corrected project association to two independent checks:
  `billing.resourceAssociations.create` on the target billing account and
  `resourcemanager.projects.createBillingAssignment` on the project. Console workflows also use
  Service Usage read permissions; the API access-control contract lists the two checks above.
- Confirmed all inspected predefined roles are GA. Billing Account Administrator contains
  `billing.accounts.setIamPolicy`, `billing.accounts.updatePaymentInfo`, and both billing/project
  association permission names; the latter project permission is ineffective when the role is
  bound only to a non-ancestor billing-account resource.
- Confirmed `billing.accounts.setIamPolicy` has custom-role support level `SUPPORTED`; billing
  custom roles are organization-defined and then applied to billing accounts.
- Corrected the Google payments boundary: `billing.accounts.updatePaymentInfo` is a documented
  cross-system exception for console access and can add/edit/fix payment methods without a separate
  payments-profile grant, but removal still requires payments-profile permission.
- Corrected audit contracts to short method names: `GetIamPolicy` is off-by-default Data Access
  despite its `ADMIN_READ` permission type; `SetIamPolicy` and optional
  `AssignResourceToBillingAccount` are always-on Admin Activity and none is an LRO.
- Added the billing-account-scoped Logging query and the official limitation that billing audit logs
  are read through the CLI or Logging API, not Logs Explorer.
- Kept association-log placement bounded: the official catalog defines the method/category/default,
  but not whether every event is stored at project scope, billing-account scope, or both.

### Removed or folded claims

- Billing-account/project enumeration: reconnaissance.
- Unlink, close, or detach operations: destructive availability/governance actions.
- Budget, anomaly, usage-export, and FinOps tampering: defense evasion, post-exploitation, or
  persistence, not privilege escalation.
- Marketplace subscriptions and commitments: financial abuse using existing authority.
- Billing-account creation: expected administration of a newly created resource, requiring
  payments-profile **Sign-up and purchase** permission when reusing an existing profile; it grants
  no control over existing billing accounts or cloud resources.
- Direct payment-info modification: sensitive but not itself a permission-acquisition primitive;
  the retained IAM self-grant covers how an attacker could acquire it.

### Evidence not claimed

- The public Cloud Billing audit catalog doesn't publish a distinct method mapping for every
  Google payments-console follow-on. No method name or Cloud Audit Logs default is asserted for
  those edits without captured or published evidence.

## 2026-09-28 independent cross-review

A separate root review re-opened the current official billing access, API access-control, project
association, payment-method, role, and audit-logging references. It independently confirmed the
billing-account/project non-inheritance boundary, the two-resource project-link check, the
`updatePaymentInfo` add/edit-versus-remove exception, the retained Billing Account Administrator
capabilities, and the short non-LRO audit method names. No additional book correction was required.
