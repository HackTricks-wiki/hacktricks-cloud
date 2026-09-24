# Secret Manager — open ideas

Open ideas — Secret Manager.

- (none open) — the managed-rotation confused-deputy hypothesis collapses into the ALREADY-documented
  "Rotation misuse" section of `gcp-secrets-manager-enum.md` (redirect the rotation Pub/Sub topic /
  modify the rotation worker via `secrets.update`). No distinct privilege-crossing effect beyond that.
  Minor optional enhancement only: the doc could name the `secretmanager.secrets.rotate` /
  `enableManagedRotation` trigger perms explicitly — a one-line addition, not a new technique.
