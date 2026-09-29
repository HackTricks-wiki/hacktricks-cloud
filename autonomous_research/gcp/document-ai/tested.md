# Document AI post-exploitation - tested research

## 2026-09-28 - official documentation and local read-only audit

No cloud resource, IAM policy, API state, or stored document was accessed or changed. The audit used current Google Cloud product, REST, IAM, and audit-logging documentation, the public v1beta3 Discovery document, and local Cloud SDK source/help where available.

### Retained

- **Dataset document extraction:** `dataset:listDocuments` returns metadata and document identifiers; `dataset:getDocument` returns a Document AI `Document`. The exact permissions are `documentai.datasets.listDocuments` and `documentai.datasets.getDocuments`. Both are `DATA_READ` Data Access methods and are disabled by default.
- **Cross-project processor-version copy:** `importProcessorVersion` lets a destination caller copy a compatible source version when the destination project's Document AI service agent already has `roles/documentai.editor` on the source project. The caller permission is `documentai.processorVersions.create` on the destination. The import is an `ADMIN_WRITE` LRO recorded in the destination project.

### Corrected or rejected

- Rejected both GCS “confused-deputy” headings. Current batch input documentation explicitly requires the requesting principal to have `storage.objects.get`, and the requesting principal needs write access to the output bucket. Cross-project P4SA access is an additional requirement, not a replacement for caller authorization.
- Corrected `listDocuments`: it returns `DocumentMetadata`, not full OCR/document content. Content retrieval requires a subsequent `getDocument` and `documentai.datasets.getDocuments`.
- Removed `processedDocumentsSets` from the technique. The permissions remain in current predefined roles, but the current public v1/v1beta3 REST surface and v1beta3 Discovery document expose no corresponding resource or callable method. It must not be presented with an invented URL.
- Bounded model import to a functional copy of an importable processor version. It does not expose raw weights, copy the dataset, or return source documents. Added type/schema, enabled-state, exact deployment-state, region/environment, supported-location, service-agent trust, and VPC-SC prerequisites.
- Folded `SetDefaultProcessorVersion` into the existing persistence cross-link instead of duplicating the durable model-pinning primitive on the post-exploitation page.
- Removed processor disable/delete/version delete/undeploy as obvious destructive availability actions rather than distinct high-value post-exploitation techniques.
- Removed processor inference against caller-readable documents as non-incremental: it provides extraction functionality but does not expand the caller's data access.

### Telemetry verified

- `google.cloud.documentai.v1beta3.DocumentService.ListDocuments` and `GetDocument` are `DATA_READ` Data Access methods and are not logged by default.
- `google.cloud.documentai.v1beta3.DocumentProcessorService.ImportProcessorVersion` is an `ADMIN_WRITE` Admin Activity LRO and is logged by default. The documented parent is the destination processor; the audit catalog does not specify a second source-project copy method.
- Optional `ListProcessorVersions` and `GetProcessorVersion` reconnaissance is `ADMIN_READ` Data Access and is not logged by default.

### Public schema and command checks

- The public v1beta3 Discovery document confirms:
  - `POST v1beta3/{dataset}:listDocuments`
  - `GET v1beta3/{dataset}:getDocument` with flattened
    `documentId.gcsManagedDocId.gcsUri` and `documentId.unmanagedDocId.docId` query parameters
  - `POST v1beta3/{parent}/processorVersions:importProcessorVersion`
  - `processorVersionSource` for a same-environment/same-region source and
    `externalProcessorVersionSource` for a different environment or region
- The same Discovery document contains no `processedDocumentsSets` method.

## 2026-09-28 - independent cross-review

The retained dataset-read and processor-version-import primitives were independently checked against the current public REST reference, IAM role index, processor-version management guide, and Document AI/Cloud Audit Logs references. No cloud API or private report was accessed.

- Confirmed that dataset `listDocuments` and `getDocument` exist only in the public v1beta3 surface, use POST and GET respectively, accept the documented flattened `DocumentId` query fields, and require only their exact dataset permissions. Document AI role grants can be scoped to the containing processor or project; the dataset authorization check inherits from that scope.
- Confirmed `roles/documentai.viewer` includes both dataset permissions while `roles/documentai.apiUser` does not. `roles/documentai.editor` and `roles/documentai.admin` include the destination `documentai.processorVersions.create` permission.
- Confirmed that the destination project's DocumentAI Core Service Agent needs `roles/documentai.editor` on the source project even for a same-project import. For a cross-perimeter import, the current guide also requires initializing a fresh destination with a dummy fine-tuning run and configuring its documented ingress/egress operations.
- Tightened audit wording: `ImportProcessorVersion` is an Admin Activity LRO authorized on the destination processor. Long-running APIs normally write start and completion records, but an immediate completion or failure can produce one record with both first/last markers. The audit catalog does not document a separate source-copy method.
