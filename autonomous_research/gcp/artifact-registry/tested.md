# Artifact Registry — tested and documentation-audited

## Previously verified live observations

- Mutable Docker tags can be moved by pushing another manifest under the same tag. The previous digest remains addressable but loses that tag. Tag immutability blocks the replacement.
- Direct REST `tags.patch` can repoint an existing mutable tag using `artifactregistry.tags.update`; the higher-level gcloud tag command tested at the time used create/delete operations instead.
- A repository-wide DENY-download rule blocked pulls while pushes and metadata listing continued. Artifact and repository deletion were also validated as availability/forensic-destruction actions.
- Anonymous Docker pulls worked after an `allUsers` reader binding propagated.
- Creating an unused predefined `gcr.io` repository reserved that namespace. The earlier shorthand “gcr.io squat needs only `repositories.create`” described only the reservation step: a complete poison-and-execute path also needs `artifactregistry.repositories.uploadArtifacts` (or another writer) to place content. The project-level Create-on-Push Writer role contains the creation and write capabilities needed for its documented first-push behavior.

These historical tests were not repeated during the 2026-09-28 documentation audit; no cloud resources were read or changed.

## 2026-09-28 — privilege-escalation page audit

The privesc page now retains only three direct escalation primitives:

1. `artifactregistry.repositories.uploadArtifacts` when a higher-privileged consumer later selects the poisoned tag/version.
2. `artifactregistry.tags.update` when an existing mutable tag can be redirected to a version already stored in the same package.
3. `artifactregistry.repositories.setIamPolicy` to self-grant a role on the target repository.

Material corrections:

- Bounded supply-chain impact to consumers that resolve and use the modified coordinate after the change. Digest-pinned workloads are unaffected, and Cloud Run resolves a tag to a digest when a revision is created.
- Removed reconnaissance permissions from the exact upload and tag-update minimums when all resource names are already known.
- Distinguished the `uploadArtifacts` publish primitive from the exact stock Docker workflow: the Docker, Python, and npm publish methods covered by the page require `uploadArtifacts`, while Docker's `Docker-HeadBlob` probe is documented with both `downloadArtifacts` (`DATA_READ`) and `uploadArtifacts` (`DATA_WRITE`).
- Distinguished direct `tags.patch` (`artifactregistry.tags.update`) from higher-level tag commands that can use `tags.create`/`tags.delete`.
- Distinguished blind `setIamPolicy` (only `repositories.setIamPolicy`) from the safe CLI read-modify-write (`getIamPolicy` plus `setIamPolicy`) and required version-3/`etag` preservation for a direct condition-safe merge.
- Replaced empirical “effectively unauditable even when enabled” wording with the current official contract. Artifact upload/download methods are Data Access and off by default, but the official audit catalog says they generate Data Access logs when the corresponding class is enabled.
- Kept exact always-on control-plane events: `UpdateTag` and `SetIamPolicy` are Admin Activity; `GetIamPolicy`, `GetTag`, and list reconnaissance are Data Access (`ADMIN_READ`).

## Folded or rejected privesc headings

- `repositories.downloadArtifacts` and `repositories.exportArtifacts`: credential/data harvesting, therefore post-exploitation rather than direct Artifact Registry privilege escalation.
- `tags.delete`, `versions.delete`, `packages.delete`, `repositories.delete`, and `rules.create`:
  denial of service, rollback destruction, or evidence destruction. Re-publishing after deletion is only a conditional extension of `uploadArtifacts`, not a standalone escalation.
- Public `allUsers` / `allAuthenticatedUsers` bindings: unauthenticated data exposure; the self-grant use of `setIamPolicy` remains on the privesc page.
- `repositories.create` gcr.io namespace claiming, attacker-controlled remote repositories, and virtual-upstream dependency confusion: already covered on the Artifact Registry persistence page.
- `repositories.update` cleanup policies, immutable-tag disabling, vulnerability-scanning changes, and logging changes: destructive or enabling operations, not independent privilege-escalation primitives. Disabling immutability matters only when chained with upload/tag permissions.
- `projectsettings.update`: legacy routing/availability control, not a privilege boundary crossing.
- Cloud Functions/App Engine “race” speculation: no verified primitive and the old text itself said stored-image replacement did not change already-running code.

## Cross-page telemetry correction

The current official Artifact Registry audit catalog classifies `google.devtools.artifactregistry.v1.ArtifactRegistry.ExportArtifact` as Data Access, not Admin Activity. The post-exploitation page now records it as an off-by-default `DATA_READ` long-running operation and no longer claims an always-on `activity` event. Its broader claim that authenticated pulls produce no audit event even after Data Read is enabled still conflicts with the current official audit contract and should be presented only as a dated environment observation, not the product baseline.

## 2026-09-28 — post-exploitation page audit

The page now retains six bounded post-compromise primitives:

1. Pull a known artifact with `artifactregistry.repositories.downloadArtifacts` and inspect it locally for sensitive content.
2. Start a server-side Cloud Storage export with `artifactregistry.repositories.exportArtifacts`.
3. Expose one repository by granting `roles/artifactregistry.reader` to `allUsers` with `artifactregistry.repositories.setIamPolicy`.
4. Disable automatic container vulnerability scanning with `artifactregistry.repositories.update`.
5. Disable Artifact Registry platform logs at repository or project/location scope with `artifactregistry.repositories.update` or `artifactregistry.projectconfigs.update`.
6. Add attacker-controlled attachment metadata using `artifactregistry.attachments.create` and, for the local-file gcloud workflow, `artifactregistry.files.upload`.

Material corrections and bounds:

- Replaced the old authenticated-pull claim with the current audit contract: Docker manifest/blob reads and package downloads are Data Access `DATA_READ`, disabled by default but emitted when the applicable class is enabled. Independently configured platform logs use log ID `artifactregistry.googleapis.com/requests` and can also record pulls.
- Kept `ExportArtifact` as an off-default Data Read LRO, but removed claims that it necessarily accepts any cross-project attacker bucket or bypasses egress/VPC-SC. The REST contract names only `exportArtifacts` on the source; destination writability and perimeter behavior remain validation prerequisites.
- Distinguished the reliable always-on `SetIamPolicy` event from subsequent accesses to a public repository. The audit contract says public resources with `allUsers` or `allAuthenticatedUsers` do not generate Data Access audit logs for resource access, while enabled platform logs are a separate signal.
- Bounded vulnerability-scanning evasion to automatic scanning of affected Docker-repository images. It does not remove existing findings or disable On-Demand/third-party scanning.
- Corrected platform-log scope and inheritance: project configuration is location-scoped and affects repositories that inherit it; an explicit repository configuration overrides it. Disabling platform logs neither deletes old logs nor disables Cloud Audit Logs.
- Bounded attachment creation to misleading consumers that trust attacker-controlled metadata without validating publisher/signature. It does not forge a signature, replace Artifact Analysis findings, or automatically satisfy Binary Authorization. The exact gcloud workflow needs both `attachments.create` and `files.upload`; `CreateAttachment` is always-on Admin Activity.

Removed or folded from the post-exploitation page:

- Repository/rule/version/package deletion and DENY-download rules: destructive availability or rollback damage rather than a focused information-gathering or defense-evasion primitive.
- Attachment deletion: destructive evidence removal and lower value than the retained metadata- integrity case; its `DeleteAttachment` Data Write behavior remains documented by the official audit catalog and can be revisited if live testing shows a distinct high-value chain.
- The VPC-SC allowance aside: a high-privilege enabler for the separate remote-repository persistence technique, not a standalone Artifact Registry post-exploitation technique.

This audit used current official Google Cloud documentation and local gcloud help only. No live Artifact Registry, Cloud Storage, IAM, logging, or scanning configuration was read or changed.

## 2026-09-28 — independent post-exploitation cross-review

No cloud resources were read or changed. All six retained techniques were rechecked against the current Artifact Registry REST, IAM, audit-logging, platform-logging, attachment, scanning, Cloud Storage audit, and local gcloud contracts.

- Clarified the platform-log hierarchy and unset-state caveat. An explicit repository setting overrides its location-scoped project setting, while clearing the repository setting restores project inheritance. The current product guide says clearing the project leaves only explicitly enabled repositories logging; current gcloud help instead labels it a fallback to organization settings or Artifact Registry defaults. The page now recommends inspecting effective state and uses explicit disable as the reliable evasion action. Severity thresholds remain independently relevant.
- Narrowed the public-resource audit exception to its documented boundary: Data Access reads of a public `allUsers`/`allAuthenticatedUsers` resource are omitted. The authenticated Admin Activity `SetIamPolicy` operation remains always-on; separately enabled platform logs can still record public requests.
- Removed an implied guarantee of destination-side Cloud Storage audit telemetry for `ExportArtifact`. The official method guarantees an Artifact Registry Data Read LRO and documents overwrite semantics, but does not publish the backend writer identity, destination IAM/VPC-SC contract, or promise a separate Storage event. Any `storage.objects.create` entry is now labelled conditional and unverified.
- Split attachment permissions by operation. Direct create against pre-existing File resources documents only `artifactregistry.attachments.create`; the shown local-file gcloud workflow first needs `artifactregistry.files.upload`. Also corrected the REST target bound to Version, Package, or Repository while noting that the shown gcloud flow expects a fully qualified version.
- Revalidated download method names, role membership for `downloadArtifacts`/`exportArtifacts`, scanning and platform-log commands, all six impact bounds, and all retained stealth categories.
