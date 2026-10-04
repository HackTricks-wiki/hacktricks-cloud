# Cloud Sql — open ideas

Open ideas — Cloud SQL.

The next questions concern permissions whose callable surface is not established.

## Resolved in independent post-exploitation cross-review (2026-09-28)

- [x] Separate Data API IAM and built-in-password minimum permissions and downstream Secret Manager logging.
- [x] Reconcile current cross-project clone support without claiming that source-only permission is sufficient for destination-side prerequisites.
- [x] Correct final-backup deletion syntax and distinguish request opt-in, instance configuration, and organization-policy enforcement.
- [x] Bound SSL downgrade impact to direct connections; Auth Proxy and Language Connectors remain encrypted regardless of `sslMode`.
- [x] Replace the nonexistent `gcloud sql instances stop-replica` command and preserve the narrower documented raw API alternative.

## New questions from 2026-09-26 audit
- [x] Check Cloud SQL `instances.setIamPolicy` / `databases.setIamPolicy` API exposure:
  the v1 and v1beta4 SQL Admin discovery documents have no such instance/database methods. No self-grant claim was published from permission names alone.
- [ ] Determine whether `backupRuns.export` can be used beyond the documented Cloud SQL-to-AlloyDB migration path. Direct GCS exfil was removed from the book because no such endpoint was found.

## Follow-ups from 2026-09-28 post-exploitation rewrite

- [x] Live-verify SQL Server `sp_help_revlogin`: enabling the flag installed the procedure without a
      restart, and the default `sqlserver` login exported a synthetic login's password hash and SID.
      Disabling the flag removed the procedure; both instances and all local client artifacts were
      deleted. Added the bounded hash-recovery technique to the post-exploitation page.
- [ ] With two disposable Workforce Identity principals, test only undocumented normalization
      boundaries: case variants, MySQL same-local-part/different-domain subjects, paired 32/63-byte
      prefixes, Unicode NFC/NFD and encoded delimiters. Exact same-subject cross-pool/provider
      crossover is already an explicitly documented limitation, not a zero-day. Stop and report
      privately only if two genuinely different mapped subjects converge on one database role.

- [ ] Test whether a supported import format can produce a useful cross-boundary disclosure beyond the documented import behavior. Arbitrary-object reads are rejected as a technique unless a parseable-file path and recoverable data flow are demonstrated.
- [ ] Compare standard Cloud SQL backup deletion with enhanced Backup and DR recovery-point retention in a disposable project. Do not claim complete recovery destruction without proving which separately managed recovery objects survive.
- [ ] Verify current audit payloads for Data API, import/export, and long-running start/completion records in a disposable instance if a future live-test budget permits. The book currently uses the official method classifications and explicitly marks engine/observability telemetry as conditional.

## Resolved (moved to tested.md)
- [x] **Live-confirm pg_cron / event_scheduler persistence** — DONE 2026-09-25. pg_cron CONFIRMED end-to-end (job fired on timer, survives IAM revocation + restart); wiki upgraded from doc-grounded to verified. MySQL `event_scheduler` left as the documented analogue. See tested.md.
