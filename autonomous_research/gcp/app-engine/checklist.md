# App Engine privilege-escalation research checklist

## Verified from current official contracts

- [x] Version creation is the code-execution boundary and uses `appengine.versions.create`.
- [x] App-level default and per-version service-account selection semantics.
- [x] Same-project restriction for a per-version service account.
- [x] Legacy App Engine default-service-account `actAs` behavior and enforcement constraint.
- [x] Current secure-by-default behavior for automatic Editor grants to default service accounts.
- [x] Supported `gcloud` deployer roles and current Artifact Registry requirements.
- [x] `--no-promote` and version-specific reachability bounds.
- [x] Fully-qualified App Engine and Cloud Build audit methods and default visibility.
- [x] App Engine LRO polling requires `appengine.operations.get` but `google.longrunning.Operations.GetOperation` is not audit logged.
- [x] Storage, Artifact Registry, request-log, and metadata-server downstream telemetry.
- [x] Flexible-only `instances.debug` behavior, core permission, SSH-key field, and LRO audit class.
- [x] Current CLI SSH helper reads and Compute/OS Login/network prerequisites.
- [x] Metadata-key and OS Login SSH branches, including the CLI's conditional `DebugInstance` behavior.
- [x] IAP support in `gcloud app instances ssh`, its Compute instance discovery permissions, and the IAP firewall source range.
- [x] Compute project/firewall, OS Login control-plane/dataplane, and IAP conditional telemetry.
- [x] Current Cloud Build `operations.get` polling permission and audit-class difference from App Engine operation polling.
- [x] Flexible service-agent identity and required role.
- [x] `versions.patch` does not update source code or the version service account.

## Open bounded validation leads

- [ ] In a disposable project with `constraints/appengine.enforceServiceAccountActAsCheck` disabled, confirm the current default-service-account deployment behavior without `iam.serviceAccounts.actAs`; repeat with the constraint enabled.
- [ ] Capture a current standard and flexible deployment to enumerate the exact staging object calls, build principal, Artifact Registry methods, and audit-entry placement for a custom per-version service account.
- [ ] Compare `gcloud app instances ssh` against direct `instances.debug` on external-IP, internal-only, metadata-key, OS Login, and IAP configurations.
- [ ] Live-confirm the OS Login branch's prerequisite that debug mode is already enabled, including whether an already-debugged instance produces any additional `DebugInstance` entry during `gcloud app instances ssh`.
- [ ] Confirm whether a direct `Instances.GetInstance` call still lands in Admin Activity exactly as the current audit catalog states.
- [ ] Re-test the historical staging-bucket manifest race only if a safe disposable deployment is available; require reproducible checksum/manifest handling before restoring it to the book.
- [ ] Re-test image tag/digest behavior during an in-flight flexible deployment; do not treat repository write access as App Engine escalation without reproducible execution of the replacement image.
- [ ] Recheck role, build-identity, and Artifact Registry requirements after future App Engine or Cloud Build default-service-account changes.
- [x] Apply the post-exploitation no-garbage bar and remove deletion plus duplicate source-modification headings; add exact stealth/telemetry metadata to all four retained disclosure families.
- [ ] In an authorized disposable repository, call `exportAppImage` with the smallest victim-side custom role, capture the actual destination writer identity and both projects' audit entries, poll the LRO, then delete the exported package/repository and verify absence. Do not use a shared destination or assume the current audit catalog's omission means silence.
- [ ] Capture Console Memcache get/set/delete/flush with App Engine Data Access disabled and enabled, confirming the published `cloud_cache.MemcacheAdminService.*` names. Use only non-sensitive marker values, restore/delete them, and never flush a non-disposable cache.
- [ ] Revisit `appengine.runtimes.actAsAdmin` only if Google exposes a callable public surface. It is currently present in broad legacy roles, unsupported in custom roles, and undocumented beyond the permission index; do not infer an admin impersonation path from its name.
