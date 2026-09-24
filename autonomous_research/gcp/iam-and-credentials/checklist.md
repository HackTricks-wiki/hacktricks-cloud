# Iam And Credentials — open ideas

Open ideas — IAM / credentials / federation.

Coverage is exhausted across three closure passes. No open actionable candidate at this time.

Generate-more triggers (only if a new IAM surface ships):
- [ ] Re-diff `gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/<p>`
  against the wiki when GCP adds new `iam.*` / `iamcredentials.*` permissions.
- [ ] Watch for new Workforce/Workload federation subresources (managedIdentities, scim*) gaining
  `setIamPolicy`-free membership levers.
