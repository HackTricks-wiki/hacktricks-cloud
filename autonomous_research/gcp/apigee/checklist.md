# Apigee — open ideas

- [ ] With an existing disposable Apigee organization, verify the minimum read permissions and exact audit classifications for KVM entry values, developer-app keys, debug sessions/masks and proxy bundle export. Do not create a paid organization for this purpose.
- [ ] Re-test link-local and private-address target validation only in a disposable owned Hybrid deployment or after Google documents a behavioral change. CVE-2025-13292 is fixed in the managed service; any managed-service bypass or cross-tenant access is a private VRP report, never a public book technique before remediation.
- [ ] Review newly added Apigee policies and extensible proxy types for attacker-controlled hostname/region fields analogous to fixed CVE-2026-2264 (`SetIntegrationRequest` `IntegrationRegion`). Test only owned backends and report any service-account token exfiltration privately.

## 2026-09-28 privilege-escalation audit

- [x] Split proxy authoring from deployment and document both deployment permission checks.
- [x] Verify the optional `iam.serviceAccounts.actAs` branch and bound runtime identity use to supported Google-auth policies and the attached service account's permissions.
- [x] Split shared-flow authoring, deployment, and environment flow-hook attachment into their exact minimum-permission path.
- [x] Replace blind environment IAM policy replacement with a policy-version-3, `etag`-preserving merge.
- [x] Map retained state changes to exact Apigee audit methods, classes, and default visibility.
- [x] Reclassify KVM, debug-session/mask, and developer-app/key operations as post-exploitation rather than generic privilege escalation.
- [x] Independently re-open the official REST authorization contracts and managed-Apigee ingress-logging boundary after the first-pass rewrite.
- [ ] With an existing disposable organization, use separate custom-role principals to live-confirm resource-level evaluation of the proxy and shared-flow dual-permission deploy paths. Do not provision Apigee solely for the test.
- [ ] With that same disposable organization, test whether attaching a proxy/shared-flow service account produces any separate IAM Credentials audit record in addition to the documented Apigee deployment and downstream target-service logs; do not assert one until observed or documented.
- [ ] Determine whether deployment-resource or Apigee Space IAM bindings authorize a distinct privilege-bearing operation that is not already captured by environment IAM. Keep them out of the book unless a concrete escalation boundary is proven.
- [ ] Audit the Preview Archive deployment workflow separately: exact `archivedeployments.*` minimums, whole-environment impact, gcloud/API operations, and audit methods. Do not conflate it with ordinary proxy revision deployment or provision an Archive environment solely for testing.
- [ ] If the post-exploitation page is next revised, move the verified KVM/debug/developer-key telemetry corrections there; do not duplicate those headings in privilege escalation.
