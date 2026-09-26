# Cloud Sql — open ideas

Open ideas — Cloud SQL.

The next questions concern permissions whose callable surface is not established.

## New questions from 2026-09-26 audit
- [x] Check Cloud SQL `instances.setIamPolicy` / `databases.setIamPolicy` API exposure:
  the v1 and v1beta4 SQL Admin discovery documents have no such instance/database methods.
  No self-grant claim was published from permission names alone.
- [ ] Determine whether `backupRuns.export` can be used beyond the documented Cloud SQL-to-AlloyDB
  migration path. Direct GCS exfil was removed from the book because no such endpoint was found.

## Resolved (moved to tested.md)
- [x] **Live-confirm pg_cron / event_scheduler persistence** — DONE 2026-09-25. pg_cron CONFIRMED
  end-to-end (job fired on timer, survives IAM revocation + restart); wiki upgraded from doc-grounded
  to verified. MySQL `event_scheduler` left as the documented analogue. See tested.md.
