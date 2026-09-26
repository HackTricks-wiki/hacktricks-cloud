# Secret Manager — open ideas

Open ideas — Secret Manager.

- (none open) — the managed-rotation confused-deputy hypothesis collapses into the ALREADY-documented
  "Rotation misuse" section of `gcp-secrets-manager-enum.md` (redirect the rotation Pub/Sub topic /
  modify the rotation worker via `secrets.update`). No distinct privilege-crossing effect beyond that.
  Minor optional enhancement only: the doc could name the `secretmanager.secrets.rotate` /
  `enableManagedRotation` trigger perms explicitly — a one-line addition, not a new technique.

## New 2026-07 managed Cloud SQL rotation feature
- [ ] Test whether `secretmanager.secrets.enableManagedRotation` alone can set a chosen password for a Cloud SQL user through a regional secret whose built-in identity holds `cloudsql.users.update`/`.list`, while the caller has neither Cloud SQL permission. Distinguish the Secret Manager permission check from the delegated identity's SQL permission check. A dedicated low-cost Cloud SQL fixture and minimum-permission caller are being used; all resources must be removed after the test.
- [ ] If enable succeeds, check whether the secret identity can target a different SQL user or instance than the configured secret was intended for, and whether the caller can learn the new password without `secretmanager.versions.access`. Escalation to a user the identity was never meant to manage could be a reportable boundary failure; a documented delegation on the configured user belongs in the book only if useful.
