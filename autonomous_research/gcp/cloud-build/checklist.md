# Cloud Build — open ideas

Open ideas — Cloud Build.

- (none open) — the gen2 `repositories.create` "shadow-repo" idea is NOT a distinct technique:
  creating a repository resource under a connection executes nothing and does not retarget existing
  triggers (a trigger binds a specific repository resource). Code execution as the build SA still
  requires `triggers.create`/`builds.create` + `iam.serviceAccounts.actAs`, OR repo-writer / PR-to-
  connected-repo — all ALREADY documented in `gcp-cloud-build-post-exploitation.md` (approval-gate
  bypass, UpdateBuildTrigger + actAs) and noted in the enum page. Cannot be lab-fired (needs external
  GitHub OAuth connection). Closed per no-garbage.

## 2026-09-28 — Open validation leads after privilege-escalation audit

These are deliberately not published as techniques without safe validation:

- [ ] Determine whether `projects.builds.retry` / `projects.locations.builds.retry` rechecks `iam.serviceAccounts.actAs` for the original build's service account. Official API documentation says retry creates a new build from an existing build but does not state whether the service-account attachment check is repeated. Test with a harmless, no-egress build and a minimally privileged custom role when live testing is authorized.
- [ ] Validate connection-level `roles/cloudbuild.tokenAccessor` inheritance to every child repository across GitHub, GitLab and Bitbucket connection types, and record provider-specific token scopes and expiry behavior without printing tokens.
- [ ] Compare push, pull-request and manual trigger controls (branch filters, comment control and approval requirements) to identify which source-writer paths actually cause execution without an additional trusted action.
- [ ] Capture representative Admin Activity entries for legacy-default and explicit-service-account builds to confirm how `iam.serviceAccounts.actAs` and resulting `CreateBuild` events correlate in current projects; do not rely on undocumented request-field redaction behavior.
