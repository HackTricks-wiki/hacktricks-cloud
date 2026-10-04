# Apigee — checked

## 2026-09-26 — service enumeration and CVE-2025-13292 status correction

- Added `gcp-apigee-enum.md` covering organizations/environments, environment-group hostnames and attachments, proxy bundles/revisions/deployments, shared flows/flow hooks, target servers/references/endpoint attachments, KVM values, API products, developer apps/keys, keystores, debug masks/sessions and resource-level IAM.
- Validated the stable `gcloud apigee` surface locally. A read-only `gcloud apigee organizations list` returned no accessible Apigee organization for the lab identity, so tenant-specific REST calls were documentation-validated and not live-fired. No Apigee resource or GCP state was created.
- Rechecked the existing `GatewayToHeaven` page against Google bulletin GCP-2026-010. The chain is CVE-2025-13292, fixed for managed Apigee in `1-16-0-apigee-3`; Google says managed customers need no action. Hybrid requires the Pub/Sub analytics pipeline and the bulletin's patched release floor. Replaced five current-looking sub-techniques with one explicitly historical/unpatched-Hybrid entry carrying impact, stealth, logs and remediation.

## Current lab constraint

The authorized project is not paired with an accessible Apigee organization. Do not provision a paid Apigee organization solely for these tests; re-run live minimum-permission checks only if an existing disposable organization becomes available.

## 2026-09-28 — privilege-escalation boundary audit

This pass was documentation- and source-validated only. No Apigee API call was sent and no cloud resource was created, changed, or deleted.

### Retained expected techniques

1. **Author and deploy a malicious API proxy revision.** A complete new-revision path needs `apigee.proxies.create` on the organization, plus both `apigee.deployments.create` on the environment and `apigee.proxyrevisions.deploy` on the revision. Specifying a proxy service account adds `iam.serviceAccounts.actAs`; it is not required for an ordinary deployment. Runtime Google-API access additionally depends on supported Google-auth policy configuration, the service account's target permissions, and the managed/Hybrid token-generation relationship.
2. **Deploy a malicious shared flow and attach it to an environment flow hook.** The distinct path needs `apigee.sharedflows.create`, both `apigee.deployments.create` and `apigee.sharedflowrevisions.deploy`, then `apigee.flowhooks.attachSharedFlow`. A hook can affect every deployed proxy in that environment at its selected hook point.
3. **Environment-scoped IAM self-grant.** `apigee.environments.setIamPolicy` can add a binding on that environment. A condition-safe workflow also needs `apigee.environments.getIamPolicy`, requests policy version 3, preserves the `etag`, and merges rather than replacing existing bindings. This is escalation only when the caller received a narrow/custom grant without the target environment permissions; `roles/apigee.environmentAdmin` already includes `setIamPolicy`, making same-scope delegation by that role generally persistence or lateral delegation.

All three retained techniques are rated **Low** stealth because the state-changing management operations are `ADMIN_WRITE` Admin Activity events that are always recorded and leave durable Apigee configuration or IAM state.

### Corrections made

- Removed stale role assumptions. The current canonical role list uses `roles/apigee.apiAdminV2`; it can author proxy/shared-flow revisions but lacks `apigee.deployments.create`. `roles/apigee.environmentAdmin` can deploy existing revisions but lacks the organization-level authoring permissions. The former blanket “API Admin can deploy” claim was therefore false.
- Corrected deployment authorization to the two-permission checks documented for both proxy and shared-flow deployment, rather than presenting only the revision deploy permission.
- Bounded service-account impact: deployment with a service account requires `iam.serviceAccounts.actAs`, but tokens are available only through supported bundle policies and runtime token-generation prerequisites, and remain limited to that service account's permissions.
- Bounded the ordinary proxy/shared-flow paths to standard Proxy deployment environments. Archive environments use a separate archive workflow and currently do not support Google authentication with service accounts.
- Replaced destructive/blind IAM-policy examples with a version-3, `etag`-preserving merge and bounded the result to the environment resource hierarchy.
- Replaced broad “no logs” claims. Management mutations are always-on Admin Activity. Managed-Apigee per-request ingress access logging is optional/Preview, Hybrid runtime visibility is operator-configured, and downstream telemetry depends on the target service.

### Rejected or reclassified hypotheses

- **KVM entry read/list and KVM write:** valuable secret access or configuration tampering, but not a direct increase in Google Cloud/Apigee authorization. Track as post-exploitation unless a concrete stronger-identity chain is demonstrated. Audit methods are `KeyValueMapService.GetKeyValueEntry` / `ListKeyValueEntries`, classified `ADMIN_READ` Data Access (not `DATA_READ`).
- **Debug session creation and debug-mask changes:** trace capture is credential/data access, not privilege escalation. `DebugSessionService.CreateDebugSession` is `DATA_WRITE` Data Access and disabled by default, contrary to the former Admin Activity claim; `DataMaskService.UpdateEnvironmentDebugMask` is `ADMIN_WRITE` Admin Activity.
- **Developer-app and app-key creation/read:** creates or exposes credentials for API-product access, but that is external/API-plane credential access rather than a generic Apigee or Google Cloud privilege escalation. `DeveloperAppKeys.GetDeveloperAppKey` is `ADMIN_READ` Data Access.
- **Deployment-resource `setIamPolicy`:** affects only the selected deployment resource and was not retained as a coequal generic self-grant primitive. It may warrant a future minimum-permission test if a concrete privilege-bearing child operation is identified.
- **Archive deployment:** not folded into the ordinary revision commands because it has a different environment mode and whole-archive workflow. It remains a separate future audit lead rather than an unverified extra book primitive.
- **Role-count matrices and keystore inventory:** useful enumeration context, not distinct privilege-escalation techniques; exact permission counts are brittle and were removed.

### Evidence sources

- Current IAM role contents: Google Cloud IAM roles/permissions reference for Apigee.
- Authorization contracts: Apigee v1 REST method pages and discovery schema for proxy/shared-flow import, deployment, flow-hook attachment, and environment IAM.
- Runtime identity prerequisites: Apigee Google authentication overview.
- Telemetry: current Apigee audit-logging method table and Apigee ingress access-logging documentation.

### Independent review

A separate root review re-opened the current official REST contracts for proxy import/deployment, shared-flow deployment, flow-hook attachment, and environment IAM. It independently confirmed the dual deploy-permission checks, optional `iam.serviceAccounts.actAs` branch, flow-hook permission, and complete-policy/field-mask semantics. It also confirmed that the documented ingress access-log feature is Preview, must be explicitly enabled, and applies to managed Apigee rather than Hybrid. No additional book correction was required after that review.
