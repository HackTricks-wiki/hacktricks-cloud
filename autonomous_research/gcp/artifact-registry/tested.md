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

## `exportArtifact` server-side exfil — DOCUMENTED (API-verified), SHIPPED
API confirmed via discovery doc: `projects.locations.repositories:exportArtifact` (POST,
`…:exportArtifact`) — "Exports an artifact to a Cloud Storage bucket"; request = {sourceVersion|
sourceTag, gcsPath}. Perm `artifactregistry.repositories.exportArtifacts` is carried by
`roles/artifactregistry.reader` (and thus `roles/viewer`). Distinct from `docker pull`: the copy is
server-side into an arbitrary (possibly cross-project attacker) bucket → bypasses registry-pull egress
controls, no container client, reader-level. Not live-fired (no distinct cost/permission block; doc-
grounded from the API surface — no false "verified" claim in the page).
**SHIPPED** → `gcp-artifact-registry-post-exploitation.md` new section
"Server-side exfil to any bucket - `artifactregistry.repositories.exportArtifacts`".
