# Artifact Registry — tested

Artifact Registry. Heavily covered (10 privesc, post-ex, persistence incl. gcr.io squat).

## VERIFIED LIVE facts
- Data plane (push/pull) is unauditable by default; even DATA_READ-on produces nothing.
- `DeleteAttachment` = DATA_WRITE off-by-default → SBOM/provenance evidence-strip is SILENT, while
  `CreateAttachment` is always-on ADMIN_WRITE.
- gcr.io squat needs only `repositories.create`; DENY-download rule = stealthy repo-wide DoS.
- Anonymous docker pull from an `allUsers` repo (unauth axis) shipped.

## Standing item (REST-only)
- `exportArtifacts` has no gcloud surface — deferred to a future REST-access pass.
