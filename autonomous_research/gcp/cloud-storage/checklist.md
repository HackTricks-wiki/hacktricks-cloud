# Cloud Storage research checklist

## Published and documentation-validated

- [x] Bucket IAM self-grant scope, helper permissions, and Admin Activity visibility.
- [x] Managed-folder IAM scope, uniform-access prerequisite, helper permissions, and audit visibility.
- [x] Project-level HMAC creation, XML-API-only impact, organization-policy blockers, and audit/metric signals.
- [x] Managed Airflow `dags/` object injection, environment-service-account boundary, and downstream logs.
- [x] Cloud Build unpinned `StorageSource` poisoning, generation semantics, two-permission overwrite requirement, build identity, and downstream logs.
- [x] Independent cross-review of IAM condition-safe updates, HMAC constraint values/quota, metric latency, Managed Airflow log conditionality, and direct/manual/retry/webhook Cloud Build telemetry.

## Rejected or folded

- [x] `storage.objects.get`: data access/post-exploitation, not automatic privilege escalation.
- [x] `storage.objects.setIamPolicy`: object ACL management with low escalation value; unavailable with uniform access and previously documented gcloud commands were invalid.
- [x] Generic `storage.objects.create` / `storage.objects.delete`: prerequisite only; retain only when a documented privileged consumer executes the object.
- [x] GCR backing-bucket poisoning: historical, not a current writable Container Registry path.
- [x] Cloud Functions/App Engine staging overwrite races: not published without a current official mutable/unpinned-source contract.

## Open leads requiring a safe lab or stronger primary evidence

- [ ] Capture current bucket and managed-folder policy-write audit entries to confirm resource-name shapes and whether additive helpers emit a separately visible IAM read entry.
- [ ] Capture HMAC create audit payload fields and correlate access ID/service-account metadata without assuming the request body is retained.
- [ ] Test new-name DAG upload with the minimum `storage.objects.create` custom role against each supported Managed Airflow generation; record parse/schedule latency and exact log names, then remove the DAG.
- [ ] Build a no-secret, no-egress Cloud Build fixture that references a reusable omitted-generation `StorageSource`; confirm when generation resolution occurs, exact source provenance, and overwrite visibility, then delete every test asset.
- [ ] Re-evaluate Cloud Run functions and App Engine only if current APIs expose an attacker-writable source object without a pinned generation or integrity check.
- [ ] Check whether `StorageSourceManifest` creates a distinct high-value mutable-manifest path; it remains Preview and needs minimum-permission, generation-resolution, and integrity testing before publication.
