# Privileged Access Manager — tested

Privileged Access Manager (PAM). 4 pages (enum/privesc/persistence/post-exp).

## VERIFIED LIVE — standalone-privesc hypothesis DISPROVEN, reframed
- Anti-delegation guard: `entitlements.create/update` offering role R requires the caller ALREADY hold `setIamPolicy` for R → PAM is NOT standalone privesc; it is persistence / attribution-laundering.
- Legacy basic `roles/owner` rejected in entitlements. No-approval entitlement auto-activates in seconds via a conditional binding titled "Created by: PAM".
- `grants.create` is not an IAM permission — conferred by entitlement `eligibleUsers` membership.
- Attribution laundering CONFIRMED: `PAMActivateGrant` is a `system_event` with NO principal; the escalating `SetIamPolicy` is attributed to the PAM service agent, not the attacker.

## 2026-09-28 — independent current-contract audit

Documentation and local stable-gcloud review only; no grant, entitlement, IAM policy, API, or service agent state was changed.

- Retained one privesc primitive: an eligible principal activates an existing entitlement that offers stronger access than its standing roles.
- Corrected requester eligibility: `allUsers` and `allAuthenticatedUsers` are not supported requester principals. Direct principals and individual members of eligible groups can request.
- Corrected the approval boundary: a requester cannot approve their own grant. An approval-gated entitlement therefore requires the configured number of distinct approvers (or separately controlled approver identities); requester control alone is insufficient.
- Bounded the result to the entitlement's resource, roles, role conditions, activation time, and duration. PAM supports Admin/Writer/Reader basic roles but not legacy Owner/Editor/Viewer.
- Confirmed stable `gcloud pam grants create` uses PAM v1 and `CreateGrant` is a non-LRO Admin Activity method. `ApproveGrant` is also Admin Activity. `PAMActivateGrant` is System Event.
- Corrected the service-agent identity by scope: `service-<PROJECT_NUMBER>`, `service-folder-<FOLDER_NUMBER>`, or `service-org-<ORGANIZATION_NUMBER>` at the `gcp-sa-pam.iam.gserviceaccount.com` domain.
- Kept entitlement creation out of privesc: Google's current required-permission table requires the matching resource `get` and `setIamPolicy` permission in addition to `privilegedaccessmanager.entitlements.create`.

Official sources:

- https://docs.cloud.google.com/iam/docs/pam-create-entitlements
- https://docs.cloud.google.com/iam/docs/pam-request-temporary-elevated-access
- https://docs.cloud.google.com/iam/docs/pam-approve-deny-grants
- https://docs.cloud.google.com/iam/docs/audit-logging/audit-logging-pam
- https://docs.cloud.google.com/iam/docs/service-agents
