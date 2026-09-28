# Cloud Monitoring research checklist

## Completed

- [x] Reconcile every retained post-exploitation technique with current official Google Cloud documentation.
- [x] Map retained reads and writes to their exact audit method, class, and default visibility.
- [x] Separate raw API minimum permissions from discovery and gcloud-helper read permissions.
- [x] Remove duplicate persistence material from the post-exploitation page.
- [x] Bound metric reconnaissance, metric injection, descriptor deletion, SLO tampering, and uptime-check impact.
- [x] Validate documented gcloud command groups locally without making API calls.
- [x] Independently recheck every retained H3 for minimum raw-API permissions versus helper-side reads.
- [x] Recheck inherited audit configuration, Metrics Scope, billing, API enablement, and point-timestamp prerequisites.
- [x] Revalidate citations, command syntax, categorical stealth, and the no-duplicate/no-garbage bar.

## Follow-up research

- [ ] In a disposable no-cost project, determine the exact extra Logging permission evaluated by each PATCH shape against a log-based alert policy; current public documentation explicitly states only the creation-side `logging.notificationRules.create` dependency.
- [ ] Capture real audit entries for each retained method to document request-field redaction or truncation without assuming the entire request body is preserved.
- [ ] Test each gcloud helper under custom roles to distinguish helper-side GET/LIST calls from the raw mutation permission.
- [ ] Test destination changes separately for every notification-channel type, including whether identity changes invalidate prior verification.
- [ ] Evaluate Metrics Scope cross-project reads with minimal permissions on scoping and monitored projects.
- [ ] Test which uptime-check fields are immutable for each monitored-resource type and which weakening changes propagate to `check_passed` alerts.
