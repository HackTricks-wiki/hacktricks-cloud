# Cloud Tasks — checked

## 2026-09-26 — Cloud Audit visibility correction (documentation review)

- The earlier lab run saw no audit entries for `CreateTask`, `RunTask`, `GetTask`, and `ListTasks` under default settings. Rechecked the [current Cloud Tasks audit logging reference](https://docs.cloud.google.com/tasks/docs/audit-logging), updated 2026-09-18: `CreateTask` (v2, v2beta2, v2beta3) is on Google's **methods that don't produce audit logs** list. Enabling Data Access logs cannot make its creation event appear. This is a stronger result than merely “Data Access off by default.”
- `RunTask` is `DATA_WRITE` (the post-exploitation page previously said `DATA_READ`); `GetTask` and `ListTasks` are `DATA_READ`. All three can produce Data Access audit logs when their categories are enabled. Queue create/update/pause/purge/delete/set-IAM-policy are `ADMIN_WRITE` and always logged.
- [Queue observability docs](https://docs.cloud.google.com/tasks/docs/monitor) say per-queue task logging defaults to sampling ratio `0.0`; enabling it records dispatch attempts but does not turn `CreateTask` into an audit event or identify the enqueuing principal from the dispatch alone.
- Corrected the three book pages, including the misleading claim that *every* Cloud Tasks post-exploitation action needs both Data Access and queue logging to leave a trace. Added per-technique stealth ratings to all 7 privesc and 4 post-exploitation headings; persistence ratings already existed.
- This was a documentation and prior-evidence audit. No GCP API mutations, lab resources, or spend; no teardown needed. No new attack primitive or 0-day claim.
