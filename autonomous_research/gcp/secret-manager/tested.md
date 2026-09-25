# Secret Manager — tested

Secret Manager. Covered (regional CMEK hijack, delayed-destroy TTL IR-defeat, regional enum blind spot).

## Replication repoint — VERIFIED LIVE as NOT possible (correctly excluded)
- `secrets.update --locations` to repoint replication → HTTP 400 "Updating secret replication is not
  supported" → replication is immutable post-create. Correctly NOT shipped.

## Standing UNVERIFIED candidate
- `secrets.rotate` / `enableManagedRotation` confused-deputy — hypothesised the rotation Pub/Sub +
  managed-rotation path could be abused as a confused deputy; **not verified, not published**.

## 2026-09-26 — audit visibility / stealth classification (documentation review)
- Rechecked the existing live-test audit observations against Google's [Secret Manager audit logging](https://docs.cloud.google.com/secret-manager/docs/audit-logging) and [Data Access configuration](https://docs.cloud.google.com/logging/docs/audit/configure-data-access) references. `AccessSecretVersion` is `DATA_READ` and is not logged by default; `AddSecretVersion`, `DestroySecretVersion`, `DisableSecretVersion`, `DeleteSecret`, `UpdateSecret`, and `SetIamPolicy` are `ADMIN_WRITE` and always recorded. No lab resource was needed or created for this classification.
- Added an explicit stealth rating to both privesc and post-exploitation Secret Manager techniques. Direct read is high stealth under the default audit configuration; destructive writes and IAM self-grants are low; generic metadata/alias updates are medium because the method is shared with ordinary changes but `updateMask` exposes the affected field. The regional CMEK technique and persistence techniques already had ratings.
- No new attack primitive found in this pass. Next audit target: apply the same per-technique visibility review to another service page; do not infer stealth only from a generic method name when a request field or resource state exposes the change.
