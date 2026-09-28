# Dataproc Metastore research checklist

## Verified from current official documentation and local CLI

- [x] Export caller/service-agent Cloud Storage write prerequisites and dump-format constraints.
- [x] Export, query, import, restore, location-mutation, and LRO polling audit methods/classes/default visibility.
- [x] Current GA CLI syntax for export, query, import, restore, and location mutation.
- [x] `QueryMetadata` read-only boundary, artifact layout, no-TTL behavior, and current CLI follow-up reads.
- [x] Import overwrite behavior, schema validation, and caller/service-agent source-read permissions.
- [x] Restore target/backup authorization split, valid backup-location structure, full versus metadata-only scope, and warehouse/IAM exclusions.
- [x] Exact `AlterMetadataResourceLocation` authorization and supported database/table/partition resource names.
- [x] Dataproc Metastore request/system platform-log names and service history/artifact downstream signals.
- [x] Removal of IAM self-grant, generic configuration discovery, and destructive deletion from post-exploitation scope.
- [x] Independent cross-review of export/import service-agent I/O, query artifact retrieval, cross-service restore, regional service versus warehouse URI semantics, and LRO record multiplicity.

## Open bounded validation leads

- [ ] In a disposable, no-production-data service, grant a custom role containing only `metastore.services.queryMetadata` and capture whether operation creators can poll/read results without separately granted `metastore.operations.get` or artifact-bucket `storage.objects.get`; current official role guidance and local CLI follow-up behavior should be reconciled with live authorization evidence.
- [ ] Capture successful and denied export audit entries when caller-only, service-agent-only, and dual `storage.objects.create` grants are tested against a disposable bucket.
- [ ] Capture `authorizationInfo`, request destination/source fields, and LRO start/completion records for all four retained primitives with Metastore Data Access logging explicitly enabled.
- [ ] Confirm whether the Metastore service agent's import and restore source reads emit successful Cloud Storage Data Access entries in the source bucket's project and record their exact principal/resource fields.
- [ ] Compare import/restore history retention and visibility after failed validation, successful completion, and service deletion.
- [ ] Verify which details from these control operations appear in `metastore.googleapis.com/requests` and `metastore.googleapis.com/system`; official docs publish the streams but not a per-operation payload contract.
- [ ] Test location repointing only with harmless synthetic Parquet/ORC/Avro content, a disposable consumer, and pre-existing read access; verify that Cloud Storage IAM is never widened and restore the original URI immediately.
- [ ] Recheck roles and audit-method mappings after future administrator-interface or Dataproc Metastore 2 changes.

## Safety and cleanup for any future live test

- Use a dedicated disposable service, catalog, bucket prefixes, custom roles, and test principals; never target production metadata.
- Record every original catalog URI/configuration before mutation and restore it before deleting test objects.
- Use `--async` only when the operation name is recorded and cleanup waits for terminal completion.
- Delete query/export/import/backup artifacts, bucket IAM grants, temporary custom roles/bindings, and the disposable service after verification; confirm no operation or resource remains in progress.
