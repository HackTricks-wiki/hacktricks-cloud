# Cloud Healthcare API research checklist

## Completed documentation and local read-only checks

- [x] Inventory stable dataset, FHIR, DICOM, HL7v2 and consent-store CLI groups.
- [x] Compare caller permissions with the Healthcare service-agent boundary.
- [x] Inspect current Healthcare predefined roles for data-plane/store-admin separation.
- [x] Map FHIR get/search/mutation, DICOMweb and HL7v2 read/ingest audit methods.
- [x] Map FHIR/DICOM/HL7v2 import and export LRO permissions and GCS/BQ prerequisites.
- [x] Correct FHIR import `enableUpdateCreate` and notification behavior.
- [x] Verify FHIR BigQuery stream configuration and service-agent destination IAM.
- [x] Verify FHIR Pub/Sub full-resource notification fields and cross-project topic IAM.
- [x] Separate consent enforcement disable from consent-store application decisions.
- [x] Verify dataset de-identification destination, same-location, permission and audit boundaries.
- [x] Add condition/etag-safe Healthcare IAM self-grant coverage.
- [x] Bound `allAuthenticatedUsers` as external authenticated—not tokenless—access.
- [x] Remove/fold destructive-only and generic CRUD headings.
- [x] Independently verify same-ID FHIR import overwrite and no-notification semantics.
- [x] Independently separate FHIR/DICOM BigQuery batch-export grants from continuous-streaming IAM.
- [x] Add safe repeated-config merge, selective cleanup, and created-grant revocation examples.
- [x] Add full `consentConfig` restore and condition/etag-safe IAM self-grant cleanup.
- [x] Make destination readback an explicit prerequisite for dataset de-identification value.

## Safe future validation

- [ ] In an isolated no-PHI store, record actual stable-v1 start/end audit entries for FHIR, DICOM,
      and HL7v2 import/export with Data Access logging enabled; confirm operation polling does not
      obscure the initiating principal.
- [ ] In isolated projects, test whether dataset-level de-identification accepts a destination in a
      different project when the caller has destination `healthcare.datasets.create`; document the
      exact service-agent/CMEK prerequisites before promoting any cross-project claim.
- [ ] Validate the minimal dataset-level IAM needed by FHIR BigQuery streaming. Official schema text
      requires the Healthcare agent's BigQuery Data Editor role; verify whether any job permission is
      exercised by the streaming implementation rather than by one-time export.
- [ ] Capture representative BigQuery telemetry from continuous FHIR streaming to determine whether
      Healthcare uses no-audit `TableDataService.InsertAll`, Storage Write API calls, or another
      internal path; do not infer per-row evidence from BigQuery's general logging defaults.
- [ ] Confirm whether a Healthcare resource policy containing `allUsers` can ever service a request
      without OAuth. Until demonstrated under the stable REST API, keep the book limited to
      `allAuthenticatedUsers` with an unrelated principal token.
- [ ] Test consent policy application and `consentHeaderHandling` only with synthetic patients and
      immediately restore the complete original consent/store configuration.
- [ ] Check FHIR deidentified-store streaming as a potential durable transformed-data tap. Retain it
      only if its separate destination permission and useful information yield clear value beyond the
      documented BigQuery/Pub/Sub mechanisms.

## Cleanup requirements for any future live test

- [ ] Snapshot full store JSON and IAM policies, including repeated configs, conditions and etags.
- [ ] Remove test stream/notification configs and restore the exact prior arrays.
- [ ] Remove service-agent grants from GCS, BigQuery and Pub/Sub destinations.
- [ ] Delete test subscriptions/topics, buckets/objects, datasets/tables and synthetic stores only
      after confirming no legitimate resource shares the target.
- [ ] Verify no Healthcare LRO remains active and no recurring delivery continues.
