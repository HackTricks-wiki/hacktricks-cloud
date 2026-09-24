# Pub Sub — tested

Pub/Sub. Thoroughly covered and largely live-verified (OIDC push-auth-SA mint, push redirect, siphon
subs, setIamPolicy, export-sink confused-deputy, snapshot capture, pinned export-write SA + actAs).

## Audit-class facts — VERIFIED LIVE
- `Subscriber.Seek` = ADMIN_READ — **IS auditable once ADMIN_READ Data Access logging is enabled**
  (page corrected; the earlier "undetectable" claim came from enabling the wrong toggle).
- Publish / Pull / StreamingPull / Acknowledge / ModifyAckDeadline are on Google's explicit
  "never audited" list regardless of config.
- Pinned-SA export-write is NOT DATA_WRITE (message delivery not audited) — mislabel corrected.

## Standing UNVERIFIED candidate
- GCS import-topic persistence: `topics.update` + `ingestionDataSourceSettings.cloudStorage` — "survives
  revocation" claim needs live confirmation. Not published.
