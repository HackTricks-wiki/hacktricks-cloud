# Artifact Registry — tested and documentation-audited

## Previously verified live observations

- Mutable Docker tags can be moved by pushing another manifest under the same tag. The previous
  digest remains addressable but loses that tag. Tag immutability blocks the replacement.
- Direct REST `tags.patch` can repoint an existing mutable tag using
  `artifactregistry.tags.update`; the higher-level gcloud tag command tested at the time used
  create/delete operations instead.
- A repository-wide DENY-download rule blocked pulls while pushes and metadata listing continued.
  Artifact and repository deletion were also validated as availability/forensic-destruction actions.
- Anonymous Docker pulls worked after an `allUsers` reader binding propagated.
- Creating an unused predefined `gcr.io` repository reserved that namespace. The earlier shorthand
  “gcr.io squat needs only `repositories.create`” described only the reservation step: a complete
  poison-and-execute path also needs `artifactregistry.repositories.uploadArtifacts` (or another
  writer) to place content. The project-level Create-on-Push Writer role contains the creation and
  write capabilities needed for its documented first-push behavior.

These historical tests were not repeated during the 2026-09-28 documentation audit; no cloud
resources were read or changed.

## 2026-09-28 — privilege-escalation page audit

The privesc page now retains only three direct escalation primitives:

1. `artifactregistry.repositories.uploadArtifacts` when a higher-privileged consumer later selects
   the poisoned tag/version.
2. `artifactregistry.tags.update` when an existing mutable tag can be redirected to a version already
   stored in the same package.
3. `artifactregistry.repositories.setIamPolicy` to self-grant a role on the target repository.

Material corrections:

- Bounded supply-chain impact to consumers that resolve and use the modified coordinate after the
  change. Digest-pinned workloads are unaffected, and Cloud Run resolves a tag to a digest when a
  revision is created.
- Removed reconnaissance permissions from the exact upload and tag-update minimums when all resource
  names are already known.
- Distinguished the `uploadArtifacts` publish primitive from the exact stock Docker workflow: the
  Docker, Python, and npm publish methods covered by the page require `uploadArtifacts`, while
  Docker's `Docker-HeadBlob` probe is documented with both `downloadArtifacts` (`DATA_READ`) and
  `uploadArtifacts` (`DATA_WRITE`).
- Distinguished direct `tags.patch` (`artifactregistry.tags.update`) from higher-level tag commands
  that can use `tags.create`/`tags.delete`.
- Distinguished blind `setIamPolicy` (only `repositories.setIamPolicy`) from the safe CLI
  read-modify-write (`getIamPolicy` plus `setIamPolicy`) and required version-3/`etag` preservation for
  a direct condition-safe merge.
- Replaced empirical “effectively unauditable even when enabled” wording with the current official
  contract. Artifact upload/download methods are Data Access and off by default, but the official
  audit catalog says they generate Data Access logs when the corresponding class is enabled.
- Kept exact always-on control-plane events: `UpdateTag` and `SetIamPolicy` are Admin Activity;
  `GetIamPolicy`, `GetTag`, and list reconnaissance are Data Access (`ADMIN_READ`).

## Folded or rejected privesc headings

- `repositories.downloadArtifacts` and `repositories.exportArtifacts`: credential/data harvesting,
  therefore post-exploitation rather than direct Artifact Registry privilege escalation.
- `tags.delete`, `versions.delete`, `packages.delete`, `repositories.delete`, and `rules.create`:
  denial of service, rollback destruction, or evidence destruction. Re-publishing after deletion is
  only a conditional extension of `uploadArtifacts`, not a standalone escalation.
- Public `allUsers` / `allAuthenticatedUsers` bindings: unauthenticated data exposure; the self-grant
  use of `setIamPolicy` remains on the privesc page.
- `repositories.create` gcr.io namespace claiming, attacker-controlled remote repositories, and
  virtual-upstream dependency confusion: already covered on the Artifact Registry persistence page.
- `repositories.update` cleanup policies, immutable-tag disabling, vulnerability-scanning changes,
  and logging changes: destructive or enabling operations, not independent privilege-escalation
  primitives. Disabling immutability matters only when chained with upload/tag permissions.
- `projectsettings.update`: legacy routing/availability control, not a privilege boundary crossing.
- Cloud Functions/App Engine “race” speculation: no verified primitive and the old text itself said
  stored-image replacement did not change already-running code.

## Cross-page telemetry correction

The current official Artifact Registry audit catalog classifies
`google.devtools.artifactregistry.v1.ArtifactRegistry.ExportArtifact` as Data Access, not Admin
Activity. The post-exploitation page now records it as an off-by-default `DATA_READ` long-running
operation and no longer claims an always-on `activity` event. Its broader claim that authenticated
pulls produce no audit event even after Data Read is enabled still conflicts with the current official
audit contract and should be presented only as a dated environment observation, not the product
baseline.
