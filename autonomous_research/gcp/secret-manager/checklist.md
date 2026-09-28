# Secret Manager — open ideas

Open ideas — Secret Manager.

- The older Pub/Sub-triggered managed-rotation hypothesis collapses into the ALREADY-documented
  "Rotation misuse" section of `gcp-secrets-manager-enum.md` (redirect the rotation Pub/Sub topic /
  modify the rotation worker via `secrets.update`). No distinct privilege-crossing effect beyond that.
  Minor optional enhancement only: the doc could name the `secretmanager.secrets.rotate` /
  `enableManagedRotation` trigger perms explicitly — a one-line addition, not a new technique.

## New 2026-07 managed Cloud SQL rotation feature
- [x] **Verified and shipped 2026-09-28.** `secretmanager.secrets.enableManagedRotation` alone can set a caller-chosen password for a Cloud SQL user through the regional secret's built-in identity. The caller had no Cloud SQL permission and no secret-version access. See `tested.md` and `gcp-secretmanager-privesc.md`.
- [x] Establish an owner control on a verified named PostgreSQL user. This succeeded with `roles/cloudsql.admin` on the control secret identity and the bare instance ID; see `tested.md`.
- [ ] Fully isolate the lower-bound permission for the secret's built-in identity. The documented two-permission custom role returned 403. A custom set with `cloudsql.instances.get`, `cloudsql.users.get`, `cloudsql.users.list` and `cloudsql.users.update` succeeded, but token-creator propagation prevented a clean three-versus-four-permission comparison in the final run. Do not call the four-permission set minimal until a new disposable secret proves the subtraction.
- [x] The initial enable call accepts the target user/instance and a caller-chosen password; no version access is necessary because the caller already knows that password. This is expected permission composition and was shipped to the book. Cross-project targeting and retargeting are not claimed: the API documents initial enablement as one-shot per secret.
