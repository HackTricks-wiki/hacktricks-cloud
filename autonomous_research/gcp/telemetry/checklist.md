# Telemetry API security research checklist

## Completed — 2026-09-29

- [x] Map normal collector and integrated-service/consumer IAM roles.
- [x] Prove minimum-permission OTLP log ingestion and backing `logging.logEntries.create` check.
- [x] Capture OTLP-to-Cloud-Logging mapping for name, severity, labels, scope and resource identity.
- [x] Test default audit visibility and service-specific audit-config support.
- [x] Restore logs, metric descriptor, IAM, identity, key, local config/files and audit policy.

## Safe follow-up frontier

- [ ] In a disposable project whose deletion is acceptable, test whether OTLP rejects every
      protected `cloudaudit.googleapis.com/*` log name. If any protected-name entry is accepted,
      keep it private and preserve the exact stored bucket/log metadata.
- [ ] With `allServices/DATA_WRITE` enabled long enough to prove a contemporaneous Monitoring
      Data Access record, repeat one OTLP log export and determine whether the Telemetry runtime is
      configurable, permanently silent, or logged under a backing service name. Use an already
      existing disposable series or another fully deletable positive control; don't create another
      retained metric point. Restore the exact prior audit policy.
- [ ] In a project with an existing disposable `_Trace` bucket, test `telemetry.traces.write` and
      compare stored resource/identity fields and audit behavior without creating new permanent
      storage.
- [x] Locate the consumer-resource IAM surface. It is gRPC-callable at
      `projects/{project}/services/{service}/consumers/{consumer}` and returns independent empty
      policies for syntactically valid names. Both Consumer Admin and Owner were denied on an
      etag-protected set despite resource-local `.setIamPolicy=true`; no binding was created.
- [ ] Recheck consumer-policy mutation only with an authorized onboarded-service fixture or public
      documentation for service/consumer IDs. If set succeeds, prove the hidden `write*` permission
      on a second principal, restore the exact empty policy, and keep any cross-project deputy
      behavior private-first.
- [ ] Negative-test a payload whose `gcp.project_id` names another authorized test project while
      the quota header and writer grant name the first project. Any cross-project destination not
      enforced by target IAM is private-first.
- [ ] Compare global and regional endpoints under a VPC Service Controls perimeter containing only
      the legacy Logging/Monitoring/Trace APIs, then with Telemetry explicitly added.

## Do not infer

- [ ] No permanent-audit-gap claim from the inconclusive short global audit-config experiment.
- [ ] No normal collector use of `telemetry.consumers.write*` without integrated-service onboarding.
- [ ] No trace write in a clean project until the resulting bucket can be removed.
