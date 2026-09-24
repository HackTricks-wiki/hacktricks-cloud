# Cloud Build — open ideas

Open ideas — Cloud Build.

- (none open) — the gen2 `repositories.create` "shadow-repo" idea is NOT a distinct technique:
  creating a repository resource under a connection executes nothing and does not retarget existing
  triggers (a trigger binds a specific repository resource). Code execution as the build SA still
  requires `triggers.create`/`builds.create` + `iam.serviceAccounts.actAs`, OR repo-writer / PR-to-
  connected-repo — all ALREADY documented in `gcp-cloud-build-post-exploitation.md` (approval-gate
  bypass, UpdateBuildTrigger + actAs) and noted in the enum page. Cannot be lab-fired (needs external
  GitHub OAuth connection). Closed per no-garbage.
