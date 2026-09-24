# Security Incident Response (security-ir) — tested

## Counter-IR (recon + exfil + case sabotage) — documented from model (service not active)

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1.
- **Availability:** `list-cases` → `SecurityIncidentResponseNotActiveException` (no active membership;
  paid enrollment, exceeds test budget). `list-memberships` → empty. So end-to-end not testable, and
  the NotActive error masks the per-resource authz gate (can't cleanly isolate it).
- **Technique (from API model — shapes unambiguous):** an attacker with `security-ir` read/write on
  an active case can:
  - **Recon:** `ListCases`/`GetCase`/`ListComments`/`ListCaseEdits` → read the responders' view of
    the intrusion (threatActorIpAddresses, impactedAccounts/Services, watchers, pendingAction).
  - **Exfil:** `GetCaseAttachmentDownloadUrl` → presigned S3 URL to download forensic attachments;
    `GetCaseAttachmentUploadUrl` → plant evidence.
  - **Sabotage:** `UpdateCase` (delete own IOCs / delete watchers), `UpdateCaseStatus`/`CloseCase`
    (ClosureCode False Positive → premature Closed), `CreateCaseComment` (disinformation).
- **Disposition:** NET-NEW page `aws-services/aws-security-incident-response-enum.md`, explicitly
  labeled "documented from the API model / requires active membership" — same from-confidence
  precedent as the QuickSight unauth page (account-not-subscribed) already in PR #413. Impact + Logs
  per technique. No infra created (service not active) → nothing to tear down.
