# Document AI post-exploitation - checklist

## Completed 2026-09-28

- [x] Reconcile processing API permissions with caller and P4SA Cloud Storage authorization.
- [x] Verify v1beta3 dataset list/get paths, query parameters, responses, permissions, and audit methods.
- [x] Separate document metadata enumeration from full stored-document retrieval.
- [x] Check current predefined-role inclusion for dataset read and processing permissions.
- [x] Verify cross-project processor import request schema, destination permission, P4SA source trust,
      compatibility/state/location constraints, VPC-SC caveat, and audit scope.
- [x] Remove undocumented `processedDocumentsSets` endpoint claims.
- [x] Fold durable default-version poisoning into the persistence cross-link.
- [x] Remove destructive-only and non-incremental processing headings.

## Safe future tests

- [ ] In a disposable custom-processor dataset containing only synthetic documents, compare
      `listDocuments` and `getDocument` with Data Access logging disabled/enabled; delete all fixtures.
- [ ] Test GCS-managed versus unmanaged dataset identifiers and confirm whether `getDocument` causes
      any backend Storage audit record in addition to the documented Document AI Data Access event.
- [ ] With two disposable projects and a synthetic custom model, validate the source/destination
      audit-log placement for same-region import, then remove the source IAM grant and both processors.
- [ ] Validate `externalProcessorVersionSource` across two supported locations, including VPC-SC
      denial telemetry, using only synthetic data and deleting all resources afterward.
- [ ] Recheck whether Google publishes a supported API for the still-listed
      `documentai.processedDocumentsSets.*` permissions before documenting them.

## Independent cross-review completed 2026-09-28

- [x] Recheck v1 versus v1beta3 availability, HTTP verbs, request fields, response content, and
      flattened `DocumentId` query syntax for both dataset methods.
- [x] Recheck dataset permission inheritance and the relevant Viewer/API User predefined-role
      boundary.
- [x] Recheck import caller permission, Editor/Admin role inclusion, destination parent, P4SA
      identity and grant scope, supported states, compatibility, location/environment, and
      single-region limitations.
- [x] Add the documented same-project P4SA-grant rule and cross-perimeter dummy-fine-tuning
      initialization prerequisite.
- [x] Recheck exact v1beta3 audit namespaces, classes, Data Access defaults, destination-parent
      placement, and LRO start/completion behavior.
- [x] Re-run scoped Markdown, command, reference, URL, and diff validation without cloud access.
