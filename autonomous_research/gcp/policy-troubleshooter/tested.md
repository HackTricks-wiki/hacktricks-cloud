# Policy Troubleshooter — tested

## 2026-09-26 — authorization and audit-contract review
- Removed the nonexistent `policytroubleshooter.troubleshoot` permission and
  `roles/policytroubleshooter.policyReviewer` role from the service, post-exploitation and IAM
  enumeration pages. Current role definitions for basic Viewer/Editor/Owner and Security Reviewer
  contain no such permission; the named reviewer role is not present in the role catalogue.
- Replaced that false single-permission model with Google's documented prerequisites. Results only
  cover policies, custom roles and group membership the caller can view; missing access produces
  partial or `Unknown` explanations. Full allow/deny, PAB, service-account principal-set and
  Workspace-group evaluation can require distinct authorities.
- Updated the CLI example to the current
  `gcloud policy-intelligence troubleshoot-policy iam` surface and the REST example to v3.
- Removed the reasoned claim that `TroubleshootIamPolicy` is a `DATA_READ` method on
  `policytroubleshooter.googleapis.com`. Google documents an internal private
  `GetEffectivePolicy` call that can appear when IAM `ADMIN_READ` logging is enabled, but does not
  publish a direct Policy Troubleshooter audit-method/category mapping in the cited references.
- The Policy Troubleshooter API is disabled in the authorized lab. Performed only service-state and
  IAM-role-catalogue reads, did not enable the API and created no resources.
