# Binary Authorization — documentation audit

## 2026-09-28 — post-exploitation taxonomy and contract review

Documentation and local CLI/source inspection only. No project state, policy, attestor, occurrence,
image, GKE cluster, or Cloud Run service was read or changed.

### Retained post-exploitation chains

1. **Project-policy relaxation plus deployment.** Kept only as a chain to an attacker-image
   deployment. `policy.update` alone is defense evasion, not post-exploitation. The GA v1 audit
   contract lists `policy.update` plus `attestors.get/list`; `policy.get` is additionally required by
   the export-first command. Impact is the resulting workload foothold, not intrinsic IAM escalation.
   The target must use the project-singleton policy; a Cloud Run service configured with a named
   `policy` resource is not weakened by changing only the singleton.
2. **Existing trusted-attestor key injection plus a valid occurrence and deployment.** Corrected the
   old claim that `attestors.update` alone suffices. Attestation creation also requires
   `containeranalysis.notes.attachOccurrence` on the backing note and
   `containeranalysis.occurrences.create` in the occurrence project. The gcloud flow also reads the
   attestor, and `--validate` checks `attestors.verifyImageAttested`. The signature is independently
   verified at admission.
3. **GKE breakglass.** Updated the example to Google's current recommended
   `image-policy.k8s.io/break-glass` Pod label. The legacy alpha annotation remains compatible but is
   not the recommended form. Retained because successful Pod admission yields a runtime foothold.
4. **Cloud Run breakglass.** Retained for immediate revision execution. The durable YAML annotation
   behavior is persistence and is not presented as the post-exploitation outcome.

### Removed or folded

- Resource-level `setIamPolicy` is a generic privesc/persistence mechanism and does not itself yield
  sensitive information or a foothold; removed from the post-exploitation page.
- Creating a new attestor was folded out because it does not affect an existing policy unless the
  attacker can also rewrite that policy. Updating a policy-referenced attestor is the distinct useful
  chain.
- Continuous Validation and platform-policy tampering were not promoted to separate H3s: disabling
  monitoring or changing another guardrail without an execution chain is defense evasion, while a
  deployment chain is already represented by policy relaxation.
- Unsigned or garbage-signature occurrence creation was rejected. Artifact Analysis accepts metadata
  storage, but Binary Authorization verifies signatures at admission.

### Telemetry conclusions

- Binary Authorization policy and attestor writes use the exact v1 management service method names,
  are non-LRO Admin Activity, and are always logged.
- The current GA gcloud flow creates the occurrence through
  `grafeas.v1.Grafeas.CreateOccurrence`; it is `DATA_WRITE` Data Access and off by default.
- `ValidateAttestationOccurrence` is `ADMIN_READ` Data Access and off by default.
- GKE Pod breakglass is an always-on Kubernetes Admin Activity event under service `k8s.io` with the
  documented breakglass marker.
- The shown GA gcloud Cloud Run update reads the service and writes it with v1 `ReplaceService`;
  direct v2 clients use `UpdateService`. The write is Admin Activity, and Cloud Run automatically
  emits a System Event on `cloud_run_revision` for every breakglass use; Google does not publish a
  stable method name for that System Event.

### Material command corrections

- Added the required PKIX signature step with `openssl dgst -sha256 -sign`; registering a public key
  without producing a matching signature is not a bypass.
- Kept image references digest-pinned for attestation semantics.
- Bounded Cloud Run deployment by its documented `get/update/operations.get`, `actAs`, deployer
  image-read prerequisite, and the Cloud Run service agent's extra cross-project image-read boundary.
