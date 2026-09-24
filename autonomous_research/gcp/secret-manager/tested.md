# Secret Manager — tested

Secret Manager. Covered (regional CMEK hijack, delayed-destroy TTL IR-defeat, regional enum blind spot).

## Replication repoint — VERIFIED LIVE as NOT possible (correctly excluded)
- `secrets.update --locations` to repoint replication → HTTP 400 "Updating secret replication is not
  supported" → replication is immutable post-create. Correctly NOT shipped.

## Standing UNVERIFIED candidate
- `secrets.rotate` / `enableManagedRotation` confused-deputy — hypothesised the rotation Pub/Sub +
  managed-rotation path could be abused as a confused deputy; **not verified, not published**.
