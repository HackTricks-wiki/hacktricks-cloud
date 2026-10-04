# Cloud Healthcare API security research

## 2026-10-04 — filtered DICOM export and Storage-read oracle check

- Reconciled the GA `filterConfig.resourcePathsGcsUri` surface with the existing export technique. The filter object contains newline-delimited study/series/instance DICOMweb paths; the Healthcare service agent needs Storage Object Viewer on it and Object Admin on the output location.
- Live-created one isolated synthetic DICOM store using Google's public sample instance, separate filter/output buckets, and a caller with exactly `healthcare.dicomStores.export` plus Service Usage Consumer. The caller was denied `healthcare.dicomStores.dicomWebRead` and direct `storage.objects.get`, yet its filtered export completed with `success: 1` and wrote exactly the selected 1 MiB instance. The store retained no broader caller data-read grant.
- Added `healthcare.operations.get` only for a separate private-first hypothesis: whether parser/LRO errors reflect arbitrary contents read from the filter URI by the Healthcare service agent. A controlled opaque canary and an invalid `/studies/<canary>` line both completed with an empty counter and no reflected content. No useful Storage disclosure oracle or vulnerability was found.
- The export produced no Healthcare audit entry under default settings, consistent with `ExportDicomData` being off-default `DATA_READ`. Dataset/store creation remained visible as Admin Activity; filter reads and destination writes are off-default Storage Data Access.
- Kept filtering as a precision/stealth refinement of the existing export technique, not a new standalone heading: the same `healthcare.dicomStores.export` permission already authorizes a full-store export.
- Deleted the DICOM instance/store/dataset, both buckets and all objects, reduced identity/key/bindings, custom role and local credentials. Revoked the newly created Healthcare service-agent binding and disabled the API; disabling removed the otherwise protected generated service-agent identity. Final inventory found zero active test resources/bindings/identities and only the normal soft-deleted custom-role tombstone.

## 2026-09-28 - official-contract and local CLI audit

No Healthcare dataset/store, IAM policy, Storage object, Pub/Sub topic, BigQuery dataset, operation, or other cloud resource was created or modified. The review used current official Cloud Healthcare REST, IAM-role, audit-log, import/export, FHIR consent, Pub/Sub, BigQuery-streaming and service-agent documentation, plus local stable `gcloud healthcare` help and read-only predefined-role metadata.

### Retained expected techniques

1. Direct FHIR get/search/create/patch/update is high-value clinical disclosure/integrity activity. The exact read audit RPC is `GetResource`, not the old `ReadResource` label.
2. HL7v2 get plus create/ingest provides a distinct message disclosure/injection boundary. The least ingestion role is `roles/healthcare.hl7V2Ingest`; discovery adds message list.
3. DICOMweb QIDO/WADO/STOW provides imaging disclosure/injection with `dicomWebRead`/`dicomWebWrite` rather than Cloud Storage permissions.
4. FHIR, DICOM and HL7v2 bulk export can copy data through the source project's Healthcare service agent. The caller needs only the store export permission; the agent independently needs the destination Storage or BigQuery permissions. This supports a controlled cross-project sink when that sink's owner grants the victim service agent access.
5. Bulk import is the reverse deputy path: the service agent reads a controlled GCS source and the API writes the target store. The three modalities have separate import permissions and exact long-running audit methods.
6. Dataset de-identification is a useful server-side copy primitive without direct record-read permission. It is bounded as de-identified output, requires source get/deidentify plus destination dataset create, and is not advertised as guaranteed unredacted or cross-project exfiltration.
7. `healthcare.fhirStores.update` can disable `consentConfig.accessEnforced`, but IAM remains fully enforced. This is a consent-layer bypass only.
8. Dataset/store `setIamPolicy` is a direct self-grant path. A dataset policy is inherited; a store policy stays store-scoped. The helper preserves version, etag and conditional bindings.
9. FHIR `streamConfigs` and full-resource `notificationConfigs` are durable store-level data taps. BigQuery and Pub/Sub destinations require the source Healthcare service agent to have independent downstream IAM, including an explicit grant for cross-project sinks.
10. An `allAuthenticatedUsers` clinical-reader binding exposes PHI to an unrelated Google identity.
    This is external authenticated exposure; current REST contracts require OAuth, so the page does
    not promise a tokenless `allUsers` request.

### Material corrections to prior coverage

- `roles/healthcare.fhirResourceReader` does **not** contain `healthcare.fhirStores.export`. FHIR Store Admin can export/configure but does not itself contain direct FHIR resource reads. Likewise, DICOM Store Admin is separate from the DICOMweb data plane, while DICOM Viewer contains read/export and DICOM Editor adds write/import.
- FHIR bulk import stores client-supplied IDs regardless of `enableUpdateCreate`; the old prerequisite was removed. Import also does not emit FHIR Pub/Sub notifications.
- `sendFullResource` and `sendPreviousResourceOnDelete` are FHIR notification fields. DICOM and HL7v2 notifications contain identifiers and are not equivalent full-record PHI feeds.
- `DeidentifyDataset` is an Admin Activity LRO because its permission set includes destination `healthcare.datasets.create`, even though it also reads/writes data. It must not be labeled only Data Access.
- Direct FHIR/DICOM/HL7v2 methods and import/export operations are Data Access and disabled by default. `UpdateFhirStore`, `SetIamPolicy`, and dataset de-identification are default-on Admin Activity. Import/export/de-identification/streaming failures can also emit default platform logs.
- BigQuery table creation is Admin Activity, but no per-row audit evidence is guaranteed for FHIR streaming. Healthcare does not name the downstream RPC; BigQuery explicitly lists legacy `TableDataService.InsertAll` as no-audit and omits `TableDataChange` for Storage Write API appends. Pub/Sub publishes and Storage object I/O are off-default Data Access.
- The Healthcare service agent does not receive automatic arbitrary access to every external bucket, dataset, or topic. Every deputy technique now states the downstream grant separately.

### Rejected, folded, or relocated claims

- Removed destructive delete, purge, rollback, and generic store/dataset CRUD headings: they are availability/evidence-destruction actions rather than distinct post-exploitation boundary gains.
- Moved Healthcare IAM self-grant from post-exploitation to privilege escalation.
- Moved FHIR BigQuery stream and Pub/Sub full-resource feeds from post-exploitation to persistence.
- Did not retain consent-store record tampering as a FHIR authorization bypass. Consent Store API decisions are a separate application-facing surface; changing a consent resource does not prove that a FHIR store is configured, has applied that policy, and will authorize the attacker.
- Did not claim `X-Consent-Scope: bypass` as an unauthenticated bypass. Its use belongs to the trusted application/authentication model and remains auditable; IAM permissions are still required.
- Did not publish a PHI-preserving `DO_NOT_TRANSFORM` de-identification recipe. Supported configs can retain useful fields, but de-identification output and failed resources are configuration-specific and do not justify calling the operation a generic full-PHI export.
- Did not claim cross-project dataset de-identification without a primary-source authorization guarantee. The API accepts a full destination name and enforces same location, but the tested book technique remains within the documented permission boundary.
- Did not keep generic notification redirects for DICOM/HL7v2 as clinical-data exfiltration: their notifications expose identifiers, not the full underlying message/image.

### Telemetry result

- Healthcare `ADMIN_READ`, `DATA_READ`, and `DATA_WRITE` methods are Data Access and disabled by default; `ADMIN_WRITE` methods are Admin Activity and default-on.
- Long-running import/export/de-identification methods can produce start/end entries when their audit class is enabled. Platform error logs are a separate default signal and do not imply a successful Data Access audit event exists.
- The service agent is the downstream principal in Storage/BigQuery/Pub/Sub logs; the Healthcare initiating audit entry, when enabled, attributes the operation to the caller.

## 2026-09-28 — independent cross-review

- Corrected FHIR import replacement semantics. A same-ID import overwrites the latest stored version without creating a historical version; the current import contract does not condition that overwrite on an incoming `meta.versionId`. Client-supplied IDs remain independent of `enableUpdateCreate`, and imports still do not emit FHIR Pub/Sub notifications.
- Expanded the BigQuery export boundary: FHIR exports resources, while DICOM can export metadata. The least-scoped grants are BigQuery Job User in the destination project and BigQuery Data Editor (WRITER) on the destination dataset; Google's documented setup grants both roles at project scope and separately calls out dataset WRITER access.
- Rechecked continuous FHIR-to-BigQuery streaming separately. The current `FhirStore.streamConfigs` schema explicitly calls for BigQuery Data Editor on the destination; unlike batch export, its contract does not explicitly require Job User. The streaming example therefore retains the dataset-scoped Data Editor grant, while the existing safe-test checklist keeps job use as a live validation question.
- Reworked both persistence examples so they refuse to reuse pre-existing destination grants, merge the repeated `streamConfigs`/`notificationConfigs` arrays, re-read before cleanup, remove only the controlled destination, and revoke only the grant they created. FHIR stores expose no etag for these updates, so concurrent changes still need explicit review.
- Added complete consent-disable cleanup. The request now preserves and restores all of `consentConfig`, including version, `consentHeaderHandling`, and access-determination logging, instead of restoring only the boolean; output-only `enforcedAdminConsents` is stripped from both update bodies.
- Strengthened the Healthcare IAM helper to refuse a pre-existing unconditional grant and to clean up with a fresh version-3 policy and etag while preserving conditions and unrelated concurrent bindings.
- Kept dataset de-identification as a bounded post-exploitation primitive, not privilege escalation: it can create a transformed server-side copy without source record-read permission, but the caller still needs modality-specific read permission inherited onto the newly created destination stores before any output can be retrieved.
- No Healthcare, IAM, Storage, BigQuery, Pub/Sub, or other cloud state was changed during this independent review.
