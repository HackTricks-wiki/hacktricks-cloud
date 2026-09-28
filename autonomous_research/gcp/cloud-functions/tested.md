# Cloud Run functions — tested and documented

## 2026-09-28 — privilege-escalation page audit

- Reduced the page from eight mixed headings to four current privilege-escalation boundaries:
  creation under a selected runtime identity, source replacement of an existing privileged
  function, source-free startup-loader injection through configuration, and build-stage execution
  under the function's Cloud Build account.
- Preserved the separate runtime and build identities. Current documentation confirms that source
  is built by Cloud Build, a custom build service account can be selected, and the Node.js buildpack
  executes attacker-controlled `build`/`gcp-build` scripts. Cloud Build documents metadata-server
  credential access for user-specified build identities.
- Bounded the runtime path by actual execution. A private 2nd-generation HTTP function does not
  automatically grant its creator invocation rights; an existing trigger, invocation permission,
  public exposure, or ordinary victim traffic must cause the malicious revision to run.
- Reconciled the two-account deployment boundary. Google's current v1/v2 deployment setup requires
  Service Account User on both the runtime and Cloud Build accounts; projects using the legacy
  Google-owned builder still have different attachment mechanics, so the effective default must be
  confirmed instead of inferred from project age alone.
- Kept the environment-only path only as a conditional primitive. `functions.update` can change
  environment configuration without a source-upload permission, but RCE requires a real runtime startup hook
  and a referenced loader already present at a readable path. `PYTHONSTARTUP` was explicitly not
  treated as universal non-interactive Python execution.
- Removed the invocation-only heading from privilege escalation. Invoking existing logic is useful
  post-exploitation but does not independently grant the function service account's IAM identity.
- Removed function-IAM public exposure from this page because it is persistence/exposure and is
  already covered by the Cloud Functions persistence page. A child function policy cannot grant
  parent-level `functions.create`.
- Removed the staging-bucket overwrite race. The old page did not establish a reproducible way to
  identify and replace the exact generation-bound upload before the managed build consumes it; the
  availability consequence alone is below the book bar.
- Removed the Artifact Registry heading because it was primarily a negative result: a running
  revision is digest-pinned, so replacing/deleting a tag does not turn it into attacker code.
- Reconciled every retained technique with current Cloud Functions, Cloud Build, buildpack, IAM,
  and audit-log documentation plus local Cloud SDK 586.0.0 help and read-only predefined-role
  inspection.
- Kept the public permission contract generation-specific: the current audit catalog maps v1
  `GenerateUploadUrl` to `cloudfunctions.functions.sourceCodeSet` and v2 to
  `cloudfunctions.functions.generateUploadUrl`. No undocumented authorization behavior is included.

This audit made no cloud mutation, created no resource, changed no IAM or API state, and produced no
cleanup debt.

## 2026-09-28 — independent cross-review

- Reconciled the current audit catalog's internally inconsistent v1 upload entry with the
  permission type and earlier live capture. `CloudFunctionsService.GenerateUploadUrl` evaluates an
  `ADMIN_WRITE` permission and was observed in always-on Admin Activity; v2
  `FunctionService.GenerateUploadUrl` is likewise Admin Activity and logged by default. The v1
  method-detail label saying Data Access is not used to override that evidence.
- Confirmed that service-account attachment produces a separate IAM Admin Activity entry with
  `protoPayload.methodName="iam.serviceAccounts.actAs"` when the backend evaluates that check. This
  is distinct from the parent Cloud Functions create/update record.
- Fixed the environment-only example to fetch and merge the existing environment-variable map. A
  safe merge adds `cloudfunctions.functions.get`; the direct field-masked update still does not need
  a source-upload permission or new source archive.
- Kept the Node.js build-hook primitive. Current buildpack documentation confirms that `gcp-build`
  executes during the build, and Google Cloud authentication documentation explicitly includes
  Cloud Build among metadata-enabled environments that can obtain an access token for the attached
  service account.
- Distinguished original-caller Cloud Functions Admin Activity from managed downstream Cloud Build
  activity, which can be attributed to a Google-managed service agent. Build stdout/stderr
  availability remains dependent on the build's logging configuration.
