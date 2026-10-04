# Config Delivery — tested

## 2026-09-28 privilege-escalation audit

Documentation-only audit; no Google Cloud project, fleet, or cluster was accessed or changed.

- Retained one complete direct-bundle chain: create bundle, create draft release, create raw-manifest variant, publish release, then create a selecting fleet package.
- Verified current v1 schema fields, semantic-version/publish lifecycle, fleet selector behavior, predefined-role contents, and `us-central1` boundary.
- Corrected audit classifications: resource-bundle/release create/update are always-on Admin Activity; variant and fleet-package creates are off-default Data Access.
- Bounded impact to selected clusters and admitted Kubernetes objects. Removed unconditional cluster-admin, privileged-pod, metadata-token, and fleet-wide claims.
- Removed generic enumeration as a privilege-escalation heading and rejected a repository/build path when the direct API gives a smaller, exact permission set.
