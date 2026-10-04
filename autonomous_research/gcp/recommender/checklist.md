# Recommender — open ideas

## Current public coverage

- [x] Move IAM recommendation/insight reconnaissance from the monolithic IAM enum into a dedicated
      post-exploitation page with exact minimum permissions, impact and telemetry.
- [x] Map all nine live MCP tools, including five state-mutation tools absent from the overview.
- [x] Retain recommendation/insight state tampering as bounded defense evasion.
- [x] Verify a write tool against only a guaranteed nonexistent UUID; do not mutate live findings.
- [x] Remove all disposable IAM, identity, credential and config state and confirm every existing
      IAM recommendation remains ACTIVE.

## Open bounded leads

- [ ] In a fixture with a purpose-created low-risk recommendation, capture ACTIVE-to-DISMISSED,
      CLAIMED, FAILED and SUCCEEDED transitions, associated insight behavior, refresh/regeneration
      timing and all console/API visibility; restore if the API exposes a supported reversal.
- [ ] Compare project, folder, organization and billing-account partial visibility for each
      recommender type in an owned hierarchy. Treat child-resource disclosure without the matching
      type-specific permission as private-first.
- [ ] Test filters, pagination, etag races and state metadata only against synthetic findings.
- [ ] Re-diff live tools against the static reference and current permission catalog each release.
- [ ] Enable MCP Data Access temporarily in a disposable project to capture exact wrapper method
      names, then restore the audit policy.
