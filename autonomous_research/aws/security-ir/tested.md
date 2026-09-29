# Security Incident Response (security-ir) — tested

## Counter-IR (recon + exfil + case sabotage) — documented from model (service not active)

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1.
- **Availability:** `list-cases` → `SecurityIncidentResponseNotActiveException` (no active membership; paid enrollment, exceeds test budget). `list-memberships` → empty. So end-to-end not testable, and the NotActive error masks the per-resource authz gate (can't cleanly isolate it).
- **Technique (from API model — shapes unambiguous):** an attacker with `security-ir` read/write on an active case can:
  - **Recon:** `ListCases`/`GetCase`/`ListComments`/`ListCaseEdits` → read the responders' view of
    the intrusion (threatActorIpAddresses, impactedAccounts/Services, watchers, pendingAction).
  - **Exfil:** `GetCaseAttachmentDownloadUrl` → presigned S3 URL to download forensic attachments;
    `GetCaseAttachmentUploadUrl` → plant evidence.
  - **Sabotage:** `UpdateCase` (delete own IOCs / delete watchers), `UpdateCaseStatus`/`CloseCase`
    (ClosureCode False Positive → premature Closed), `CreateCaseComment` (disinformation).
- **Disposition:** NET-NEW page `aws-services/aws-security-incident-response-enum.md`, explicitly labeled "documented from the API model / requires active membership" — same from-confidence precedent as the QuickSight unauth page (account-not-subscribed) already in PR #413. Impact + Logs per technique. No infra created (service not active) → nothing to tear down.

## Membership/account boundary and telemetry re-audit

- **Date:** 2026-09-29. Lab account `228478051196`, both allowed Regions.
- **Validated boundary:** exact-resource IAM simulation and safe failed-call telemetry support the `BatchGetMemberAccountDetails` known-candidate organization/coverage oracle. The request is a read management event containing all candidate account IDs; response data is not stored in CloudTrail.
- **Documented expected attacks:** exact-membership `UpdateMembership` can disable triage/remove OU coverage; `CancelMembership` immediately destroys membership and historical-case access; the management account can terminate delegated deployments with `organizations:DeregisterDelegatedAdministrator` for `security-ir.amazonaws.com`.
- **Corrections:** sensitive case/contact/attachment fields and presigned URLs are redacted or absent from CloudTrail; attachments are a self-managed-case workflow; member accounts and email participants gain no IAM access; no resource-policy-based direct cross-account access exists.
- **Negative:** no anonymous API, known-ID bypass, watcher escalation, CloudTrail URL leak or proven containment-role confused deputy. No zero-day report.
- **Cleanup:** memberships remained empty in both Regions. No cases, attachments, IAM/containment roles, service-linked roles, Organizations settings or other resources were created or modified; temporary output was deleted.
