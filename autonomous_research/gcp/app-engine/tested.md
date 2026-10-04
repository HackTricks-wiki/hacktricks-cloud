# App Engine privilege-escalation research tested

## 2026-09-28 documentation and CLI audit

Scope was current official documentation, API references, and local Google Cloud CLI 586.0.0 help/source inspection. No Google Cloud resource was created, modified, or deleted.

### Retained escalation primitives

- Creating an attacker-controlled App Engine version to execute as its app-level default or same-project per-version service account.
- Enabling debug and injecting an SSH key into a running flexible-environment VM to obtain guest execution and the attached version service account.

### Material corrections

- Replaced the old observed deployment permission list with the actual boundary (`appengine.versions.create`), the service-account attachment check, and Google's current supported `gcloud` role prerequisites for Cloud Build and Cloud Storage.
- Preserved the important legacy exception: organizations still affected by App Engine's old behavior must enforce `constraints/appengine.enforceServiceAccountActAsCheck` to require `iam.serviceAccounts.actAs` for the default service account. Google says the constraint is visible only in affected environments; an absent constraint means the check is already enforced. Explicit user-managed/per-version identities still require `actAs` and must be in the same project.
- Bounded the impact of default-service-account execution. The appspot account can retain Editor in older projects, but secure-by-default organizations prevent the automatic grant and many projects have downscoped it.
- Corrected current Artifact Registry prerequisites: standard deployment identities need upload access; flexible deployment identities need both download and upload access.
- Replaced shorthand audit names with fully-qualified `google.appengine.v1.Versions.CreateVersion`, `google.appengine.v1.Instances.DebugInstance`, Cloud Build `CreateBuild`, and the documented downstream Storage/Artifact Registry classes.
- Added the helper-only `appengine.operations.get` prerequisite. App Engine's current audit catalog explicitly says its `google.longrunning.Operations.GetOperation` polling call produces no audit log; Cloud Build `GetBuild` is Data Access (`ADMIN_READ`) and disabled by default.
- Added automatic App Engine request logs as a detection signal when a no-traffic version is invoked by HTTP.
- Reduced the SSH helper permissions to known-ID calls and separated the core `instances.debug` permission from CLI discovery, Compute project/firewall checks, OS Login, IAP, and network prerequisites. OS Login on the service-account-backed VM also needs `iam.serviceAccounts.actAs`; IAP needs `iap.tunnelInstances.accessViaIAP`.
- Added conditional downstream SSH telemetry: IAP `AuthorizeUser` and OS Login `CheckPolicy` are Data Access signals disabled by default, while guest shell commands are not Cloud Audit events.
- Recorded the audit catalog's non-obvious classification of `google.appengine.v1.Instances.GetInstance` as Admin Activity despite the REST method requiring `appengine.instances.get`.

### Removed or folded headings

- Environment-variable startup injection: folded into arbitrary version deployment. The deployer already controls code/config; interpreter hooks add no App Engine IAM escalation boundary unless an external CI wrapper creates a separate input-validation bug.
- Application default-service-account update: not independent. It affects only subsequently deployed versions and still needs a deployment to execute; a per-version service account can be selected during that same deployment.
- `appengine.versions.update`: removed as a false code/identity escalation path. The current patch contract supports serving, scaling, and instance-class fields, not source code or the version service account.
- Dispatch routing: removed from privilege escalation. It requires an already-controlled destination service and is traffic interception/persistence rather than a new Google Cloud identity boundary.
- Source/config viewing and `getFileContents`: removed from privilege escalation because they are post-exploitation data disclosure and are already documented on the App Engine post-exploitation page.
- Destructive service/version operations: not privilege escalation.
- Staging-bucket overwrite race: removed from the book page because the current supported contract exposes checksummed deployment files but does not guarantee a mutable timing window; the historical third-party PoC is not sufficient current primary evidence.
- Artifact Registry image overwrite race: removed as speculative. Current documentation provides no contract that replacing repository content changes an already deployed App Engine version.

### Official contracts reviewed

- App Engine IAM roles, service-account assignment, deployment, routing, metadata server, and debug/instance REST references.
- App Engine, Cloud Build, Artifact Registry, and Cloud Storage audit catalogs.
- Current Artifact Registry migration prerequisites for App Engine standard and flexible environments.
- Local `gcloud app deploy`, `gcloud app update`, `gcloud app instances enable-debug`, and `gcloud app instances ssh` help plus the installed SSH helper's API-call sequence.

## 2026-09-28 independent cross-review corrections

- Confirmed that the legacy no-`actAs` exception is limited to the auto-created App Engine default service account. A user-managed app-level default and every explicitly selected per-version account remain subject to `iam.serviceAccounts.actAs`; the legacy organization-policy constraint is visible only where the exception still exists.
- Split human deployment, App Engine version identity, Cloud Build, staging, and flexible service-agent prerequisites. The App Engine deployment/version service account needs current Artifact Registry access, while the caller needs the documented App Engine, Storage, and Cloud Build deployment roles. Flexible deployment also depends on the Google-managed flexible service agent retaining `roles/appengineflex.serviceAgent`.
- Corrected current Cloud Build polling: the installed CLI submits with `cloudbuild.builds.create` and its synchronous path polls `google.longrunning.Operations.GetOperation` with `cloudbuild.operations.get`; some inspection/parallel paths use `cloudbuild.builds.get`. Cloud Build's polling method is Data Access, unlike the same App Engine LRO method, which App Engine explicitly does not log.
- Bounded targeted no-promotion invocation: version-specific `appspot.com` URLs bypass dispatch rules but not ingress, App Engine firewall, or application/handler authentication. HTTP invocation creates an App Engine request log by default; startup-only execution need not.
- Corrected flexible debug behavior: the debug VM is removed from health-checking pools but remains in the load-balancer pool and receives requests; automatic OS updates and patches are disabled during debugging, and enable/disable is written to guest syslog.
- Separated SSH credential branches in Google Cloud CLI 586.0.0. The metadata-key branch calls `DebugInstance` and needs `appengine.instances.enableDebug`, without Compute metadata-write permissions. If OS Login is enabled, the helper does not use `DebugInstance` merely to inject the key; it uses an OS Login profile/import or instance-bound signed certificate, and debug mode must already be enabled or be enabled separately.
- Added exact helper reads and conditional access: App Engine version/instance reads, Compute project/firewall reads, OS Login roles plus service-account `actAs`, and IAP's tunnel permission plus Compute instance get/list and IAP firewall range.

## 2026-09-28 — post-exploitation taxonomy and telemetry audit

- Rebuilt the page around four verified disclosure/foothold families: Memcache reads/poisoning, application-log reads, full version configuration, and retained source. Removed service/ version deletion as destructive availability-only behavior and source modification as a duplicate deployment privilege-escalation/persistence action.
- Corrected Memcache telemetry. Current official docs classify Console `GetMemcacheItem` as Data Read and set/delete/flush as Data Write, all off by default; application-originated bundled Memcache calls are explicitly not audit logged. The old categorical “no logs” claim was false for Console operations.
- Corrected version `GetVersion`/`ListVersions` from `DATA_READ` to `ADMIN_READ` Data Access and kept their independent raw-permission boundary. `view=FULL` can return literal environment values, runtime identity and source locations, but does not grant the referenced Storage object.
- Bounded source review: `getFileContents` remains a Console-only permission absent from the public REST discovery, while the scriptable path needs version metadata plus separate `storage.objects.get` and can fail after staging-object cleanup. Catalog omission is recorded as undocumented telemetry, not proof of silence.
- Rechecked `exportAppImage` against the current v1 discovery document. The method and fully qualified Artifact Registry destination are real, but the public contract does not document the export service identity or complete cross-project destination checks. The prior reasoned always-on Admin Activity claim was removed because the current App Engine audit catalog omits the RPC; live victim/destination telemetry and minimum destination authorization remain open tests. Because those are material prerequisites, the candidate remains in this ledger and checklist and was removed from the book until verified.
- Documentation, discovery-schema, role and read-only existing-application inventory only. No App Engine version, repository, image, IAM binding or service configuration was created or changed.
- Assessed `appengine.runtimes.actAsAdmin`, which remains in broad legacy Viewer-style roles but has no documented public API/CLI method and is not supported in custom roles. It is not promoted as a runtime-admin impersonation primitive without a callable surface or demonstrated boundary.
- Expanded telemetry to include Compute helper reads, OS Login `ImportSshPublicKey`/`SignSshPublicKey`, guest `CheckPolicy`/2FA methods, IAP `AuthorizeUser`, and the no-audit OS Login profile/key-maintenance methods.
