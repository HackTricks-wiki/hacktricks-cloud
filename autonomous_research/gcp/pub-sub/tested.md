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

## GCS import-topic message injection / persistence — TESTED, SHIPPED

Hypothesis: a principal who can create/reconfigure a Pub/Sub topic to ingest from a Cloud Storage
bucket they control can inject arbitrary messages into every subscriber by dropping objects.

Live test (lab `gcp-labs-eqd4ny8d`, all infra torn down):
- Created an import topic with `--cloud-storage-ingestion-bucket=<bkt> --cloud-storage-ingestion-input-format=text`.
- Required grants to the Pub/Sub service agent (`service-<PNUM>@gcp-sa-pubsub`): `roles/storage.admin`
  on the bucket **and** `roles/pubsub.publisher` on the topic. Missing the publisher grant → ingestion
  state `PUBLISH_PERMISSION_DENIED`, no delivery. After granting → state `ACTIVE` (~75 s to flip).
- Dropped text objects; every newline-delimited line arrived as its own message on a pull subscription.
  Confirmed BOTH the one-time backfill of pre-existing objects AND ongoing delivery of new objects.

**Result:** genuine standing message-injection / pipeline-poisoning + persistence primitive, distinct
from the documented export-**sink** (this is ingest/injection, the opposite direction). `topics.create`
and `topics.update` are in `roles/pubsub.editor` and `roles/editor`. Source bucket can be cross-project
(attacker's own project), so the injection origin lives outside the victim boundary.
**SHIPPED** → `gcp-pub-sub-post-exploitation.md` new section
"`pubsub.topics.create` / `pubsub.topics.update` — import-topic (Cloud Storage ingestion) message injection".

## 2026-09-26 post-exploitation quality and visibility audit

- Reconciled all retained Pub/Sub post-exploitation techniques with the current official audit table.
  Corrected stale statements that `Publish`/`Pull` were merely disabled-by-default (Google explicitly
  excludes these message methods even when Data Access logging is enabled) and restored the verified
  `Seek` classification: `ADMIN_READ`, disabled by default but auditable when that exact toggle is on.
- Added exact minimum permissions and categorical stealth ratings to all 16 retained techniques.
- Removed the standalone `pubsub.schemas.delete` entry because the page itself established that it did
  not bypass validation and labelled it useless. Removed the standalone schema `setIamPolicy` entry
  because it had no impact without the separately documented topic-update/schema-attachment chain.
  These permission facts remain known but do not meet the book's technique-quality threshold.
- Documentation/official-reference pass only; no Pub/Sub or other cloud resource was created.
