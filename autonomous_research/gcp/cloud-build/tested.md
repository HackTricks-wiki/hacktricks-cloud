# Cloud Build — tested

Cloud Build. Fully covered (build-step RCE, `connections.setIamPolicy`→SCM token, workerpools egress).

## Standing UNVERIFIED candidate — GAP A
- `cloudbuild.repositories.create` shadow-repo: hypothesis that creating a repository resource under
  an existing 2nd-gen connection could redirect/point a trigger at attacker source. Flagged repeatedly
  as **"would be garbage if it silently fails"** — never live-fired. See checklist.
