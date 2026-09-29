# Container Analysis / Artifact Analysis — tested

Last reviewed: 2026-09-28

## Retained book techniques

- Privilege escalation: note-level `setIamPolicy` self-grant (1 H3).
- Post-exploitation: occurrence/note metadata recovery and valid attestation creation with all three required boundaries (2 H3s).
- Persistence: a hidden-from-project-IAM note binding and an attacker-controlled attestor/key trusted by Binary Authorization policy (2 H3s).

## Prior live evidence

- A synthetic ATTESTATION occurrence with garbage signature bytes was accepted by the Artifact Analysis storage API. This proves storage-time signature validation is absent; it **does not** prove a Binary Authorization bypass. The enforcer validates against the attestor's registered public keys at admission.
- A direct note `SetIamPolicy` self-grant succeeded and read back on that note. The policy was restored and all synthetic note/occurrence fixtures were deleted.
- Under the project's then-default audit configuration, the note policy write appeared as `google.devtools.containeranalysis.v1.ContainerAnalysis.SetIamPolicy` in Admin Activity, while the synthetic create/list operations produced no entries. The current official audit catalog independently classifies v1 Grafeas reads/writes as disabled-by-default Data Access.
- No cloud state was read or mutated during the 2026-09-28 documentation correction.

## Material corrections in the 2026-09-28 review

- Current v1 occurrence create/update/delete methods require the occurrence permission **and** `containeranalysis.notes.attachOccurrence` on the provider note. An ordinary occurrence editor in the consumer project therefore cannot mutate scanner findings whose notes are owned elsewhere.
- The occurrence `details` union is immutable. Vulnerability `severity`, `cvssScore`, `cvssVersion`, descriptions, related URLs and fix-availability fields are additionally output-only. The `cvssv2`/`cvssv3` structures are not themselves marked output-only, so the old blanket “CVSS fields” wording was too broad; immutable details still make `updateMask=vulnerability.severity` an unsupported downgrade path.
- Removed vulnerability suppression from both post-exploitation and persistence. The earlier live work proved writes on attacker-controlled synthetic notes/occurrences, not mutation of a Google-owned vulnerability occurrence.
- Reframed attestation creation: `occurrences.create` plus note attachment can store arbitrary bytes, but useful admission additionally requires a valid signature from a key registered on an attestor required by the applicable Binary Authorization rule.
- Corrected v1 Grafeas audit method names (`grafeas.v1.Grafeas.*`) and documented the separate Binary Authorization validation and platform-deployment evidence.
- Corrected the predefined-role boundary: `roles/iam.securityAdmin` currently includes `containeranalysis.notes.setIamPolicy`; Editor and Notes Editor do not.
- Replaced destructive IAM-policy examples with version-3/etag-preserving read-modify-write and exact-policy restoration. The restoration now uses the etag returned by the add, so it fails on a later concurrent change instead of fetching a fresh etag and overwriting that change.

## Rejected or folded ideas

- **Downgrade a scanner finding's severity:** rejected; occurrence details are immutable and the severity field is additionally output-only.
- **Delete/update any vulnerability occurrence with only `occurrences.editor`:** rejected for v1; the provider-note attachment permission is also evaluated.
- **Garbage-signature occurrence bypasses Binary Authorization:** rejected; storage accepts it but the enforcer verifies the signature.
- **Occurrence deletion as persistence:** rejected as destructive cover-up rather than persistence, and the old authorization premise was incomplete.
- **SBOM export as a separate disclosure H3:** folded into metadata recon. Occurrence metadata can disclose an SBOM's Storage location, but object download is a separate Storage authorization boundary.

## Official evidence used

- Artifact Analysis REST resource schemas and current IAM role catalog.
- Artifact Analysis audit catalog, including v1 Grafeas methods and dual occurrence/note authorization.
- Binary Authorization attestation creation, concepts, multi-project setup, permissions and audit catalog.
- SBOM storage/reference documentation.

## Independent cross-review — 2026-09-28

- Re-checked every retained boundary against the current v1 Grafeas, Binary Authorization and Cloud KMS audit catalogs, the current occurrence schema, stable gcloud 586.0.0 source/help, and local predefined-role output. No cloud resource was read or mutated.
- Corrected the vulnerability wording: the occurrence `details` union is immutable, but `cvssv2`/`cvssv3` are not individually marked output-only. The conclusion remains unchanged:
  occurrence update cannot replace vulnerability details.
- Made note-IAM cleanup concurrency-safe. The previous example fetched a fresh etag before writing the old policy, which could erase an intervening legitimate change. Cleanup now uses the etag returned by the controlled add and fails on any later mutation.
- Added the missing multi-project trust edges: the deployer Binary Authorization service agent needs `roles/binaryauthorization.attestorsVerifier` on the attestor, while both attestor and deployer service agents need `roles/containeranalysis.notes.occurrences.viewer` on the note. These imply attestor/note `setIamPolicy` during setup unless the bindings already exist.
- Confirmed the stable gcloud Binary Authorization surface uses v1. The current permission reference says direct `UpdatePolicy` requires `binaryauthorization.policy.update`; preserving an existing policy also needs `policy.get`. The generated v1 audit catalog additionally lists `attestors.get`/`attestors.list` in UpdatePolicy authorization metadata, although the current predefined Policy Editor role does not contain them; this documentation discrepancy remains an evidence item, not an invented minimum caller permission.
- Split downstream telemetry correctly: GKE enforcement outcomes appear in cluster Admin Activity, Cloud Run enforcement outcomes can appear as revision System Event logs, and `PlatformPolicyEvaluationService.EvaluateGkePolicy` itself is explicitly a no-audit-log method.
