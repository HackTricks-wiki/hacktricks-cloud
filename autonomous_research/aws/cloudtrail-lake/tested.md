# CloudTrail Lake (cloudtrail-data) — tested

## PutAuditEvents channel poisoning — VERIFIED (authz gate) / end-to-end blocked

- **Date:** 2026-09-24. Lab acct 228478051196, us-east-1.
- **Hypothesis:** `cloudtrail-data:PutAuditEvents` lets a caller inject arbitrary forged events into a
  CloudTrail Lake custom-integration channel → anti-forensics (misattribution / burying real events)
  + ingestion-cost inflation. Zero prior wiki coverage (`cloudtrail-data` = 0 hits).
- **End-to-end BLOCKED:** `create-event-data-store` → `InvalidParameterException: CloudTrail Lake is
  no longer accepting new customers`. Cannot build an EDS/channel in the lab, so injection-lands
  couldn't be observed.
- **Authz gate VERIFIED:** least-priv role with ONLY `cloudtrail-data:PutAuditEvents` → calling
  `put-audit-events` against a bogus channel ARN returns **`ChannelNotFound`** (resource error), NOT
  `AccessDenied`. Confirms the IAM identity-policy gate is that single action; channel resource
  policy is the additional/alternative auth path for cross-account partners.
- **Disposition:** NET-NEW, documented as a scoped section in `aws-cloudtrail-post-exploitation`
  (Bypass Detection family). Honest scope: events land in the CUSTOM EDS categorized as non-AWS
  `ActivityAuditLog` — they do NOT forge into the AWS-managed API-activity store; value is polluting
  cross-store Lake queries + cost. Precondition: existing Lake custom channel (Lake closed to new
  customers). Verified-gate + doc-scoped mechanism, same honesty pattern as AppFabric.
- **Teardown:** probe role deleted, verified NoSuchEntity. No EDS was created (creation errored).
