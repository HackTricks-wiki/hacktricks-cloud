# Contact Center Insights — tested research ledger

## 2026-09-28 — post-exploitation documentation audit

No live cloud resources were read, created or modified. The pass used the current v1 discovery document, predefined-role descriptions and current official Customer Experience Insights, Cloud Storage, BigQuery and Cloud Logging documentation.

### Retained techniques

- **Stored transcript and analysis reads:** retained as direct high-value disclosure. `GetConversation`, `ListConversations`, `GetAnalysis` and `ListAnalyses` are `DATA_READ` Data Access and disabled by default. `ListConversations` must explicitly request `view=FULL`; `GetConversation` defaults to `FULL`.
- **Signed raw-audio URLs:** retained separately because it exposes backing audio as a bearer capability. Corrected the REST method from POST to GET, the RPC name to `GenerateConversationSignedAudio`, and the response path to `signedAudioUris`. The permission is present in the current Viewer role.
- **Cloud Storage service-agent read:** retained with a strict supported-format bound. `CreateConversation` can read a supported GCS transcript through the Insights service agent and explicitly does not transcribe or redact. This is not an arbitrary-object byte-read. Upload/ingest variants have different transcription/redaction and LRO behavior.
- **Cross-project BigQuery export:** retained. The current method contract authorizes location export with `contactcenterinsights.conversations.list`; the separately named `.conversations.export` permission is not the v1 method check. The destination table must exist, be location compatible and be writable by the Insights service agent.

### Material corrections

- Reclassified all Customer Experience Insights resource methods used by the page from claimed Admin Activity to their official Data Access categories. Only IAM `SetIamPolicy` is `ADMIN_WRITE` in the current service audit matrix.
- Corrected the signed-audio permission boundary: project-wide Viewer already contains `conversations.generateSignedAudio`; dataset and authorized-view variants have separate scoped permissions.
- Corrected signed-URL telemetry: a Cloud Storage XML API object GET is eligible for `storage.objects.get` Data Access logging when enabled; it is not categorically outside Cloud Audit Logs.
- Bounded GCS deputy impact to supported transcript/audio formats that Insights can parse and store. Removed the “any arbitrary object” claim.
- Corrected export authorization, LRO behavior, existing-table/location prerequisites, default `WRITE_TRUNCATE`, and destination telemetry. BigQuery Data Access logs cannot be disabled.
- Removed destructive delete headings, configuration persistence and analysis creation as standalone post-exploitation primitives.

### Adjacent-page observations

- The enum page still carries the old arbitrary-object wording, uses a mutating service-identity creation command under enumeration, and attributes export to `.conversations.export`; it should be reconciled in a dedicated enum pass.
- The persistence page still classifies analysis-rule and settings writes as Admin Activity. The current audit catalog classifies those resource writes as disabled-by-default Data Access. Its redaction heading also needs to be bounded to the documented upload/ingest paths and per-request override behavior.
- No current Contact Center Insights privilege-escalation or unauthenticated-access page was present.

### Evidence inspected

- Current v1 REST discovery schemas/methods for conversation views, signed-audio response fields, create/upload/ingest/export and Settings.
- Current `roles/contactcenterinsights.viewer`, `editor`, `admin` and `serviceAgent` predefined-role descriptions.
- Official Insights audit-method catalog and Data Access defaults.
- Official import, audio-playback, BigQuery-export and V17 export-schema guides.
- Official Cloud Storage signed-URL/audit and BigQuery audit-log contracts.

## 2026-09-28 — independent reciprocal review

- Rechecked the 100,000 maximum list page size, `BASIC` versus explicit `FULL` views, Viewer role contents, exact v1 audit methods and disabled-by-default Data Access behavior.
- Rechecked signed audio as a Preview GET/bearer capability and confirmed that signed-URL XML GETs are eligible for Cloud Storage Data Access logging when enabled. Normalized categorical Stealth labels and added the Preview bound.
- Rechecked the supported-format limit on direct GCS-source creation and the absence of an arbitrary-byte response path.
- Rechecked cross-project export's `conversations.list` permission, pre-existing table/location, default truncation, service-agent destination IAM, and non-disableable BigQuery Data Access evidence. No correctness issue remained after those bounds.
- Validation passed for Bash, JSON construction, four H3 metadata/log tables, references, details/ fences, official URLs and `git diff --check`. No cloud state was accessed or mutated.
