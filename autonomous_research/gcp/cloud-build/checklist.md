# Cloud Build — open ideas

Open ideas — Cloud Build.

- [ ] **GAP A — `repositories.create` shadow-repo (UNVERIFIED, needs supervised live-fire).**
  Create a `Microsoft`-equivalent repository resource under an existing Cloud Build 2nd-gen connection
  the attacker can read; test whether a trigger can then be pointed at an attacker-controlled repo/ref
  without holding `connections.create`/`triggers` write on the victim's original repo. Confirm the
  effect actually changes what source a build pulls (not a silent no-op). Min-perm to pin:
  `cloudbuild.repositories.create` (+ which predefined role carries it). Move to tested.md with the
  result; only ship to the wiki if it genuinely redirects build source.
