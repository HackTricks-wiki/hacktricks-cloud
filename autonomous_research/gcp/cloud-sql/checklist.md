# Cloud Sql — open ideas

Open ideas — Cloud SQL.

No open actionable candidates. All known primitives verified or documented.

## Resolved (moved to tested.md)
- [x] **Live-confirm pg_cron / event_scheduler persistence** — DONE 2026-09-25. pg_cron CONFIRMED
  end-to-end (job fired on timer, survives IAM revocation + restart); wiki upgraded from doc-grounded
  to verified. MySQL `event_scheduler` left as the documented analogue. See tested.md.
