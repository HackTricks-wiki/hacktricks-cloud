# Binary Authorization research checklist

## Completed

- [x] Reclassify management-only policy/IAM claims under the post-exploitation foothold taxonomy.
- [x] Verify current GA Binary Authorization management audit methods and classes.
- [x] Verify Artifact Analysis occurrence permissions and audit class.
- [x] Verify current GKE breakglass field and documented audit query.
- [x] Verify Cloud Run breakglass permissions, command, and default logging.
- [x] Validate local `gcloud` attestation and public-key command flags.

## Safe future checks

- [ ] In a disposable enforcing project, test whether GA v1 `UpdatePolicy` evaluates
  `attestors.get/list` for an `ALWAYS_ALLOW` body with no attestor references; current public audit
  contract lists both permissions, so the book conservatively includes them.
- [ ] Capture the exact Cloud Run breakglass event payload fields for v2 `UpdateService` and compare
  the event with the ordinary Admin Activity record.
- [ ] Confirm in a disposable GKE cluster that Continuous Validation continues reporting a running
  image after the project-singleton admission policy is relaxed; platform policies monitor rather
  than reject the deploy.

All future tests require disposable workloads and immediate policy, attestor, occurrence, image, and
workload cleanup.
