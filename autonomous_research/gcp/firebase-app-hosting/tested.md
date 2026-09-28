# Firebase App Hosting — tested

## 2026-09-28 privilege-escalation audit

Documentation/schema-only audit; no Firebase, Cloud Build, Cloud Run, or Artifact Registry resource was accessed or changed.

- Verified the v1 discovery schema accepts an Artifact Registry container image as a Build source and requires an existing Build name in a Rollout.
- Retained the existing-backend chain requiring only `builds.create` plus `rollouts.create`; it does not require a backend update or caller `actAs`.
- Verified both permissions are present in `roles/firebaseapphosting.developer` and bounded impact to the backend's already-configured service account.
- Removed speculative environment-variable injection and the conflated service-account-change path.
- Recorded exact discovery method IDs; managed Cloud Build/Cloud Run rows are conditional on those stages actually occurring.
