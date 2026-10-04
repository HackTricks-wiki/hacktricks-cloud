# Deployment Manager — tested and assessed

Last updated: 2026-09-28

## Scope and environment

- Audited the privilege-escalation page, current V2 REST surface, predefined roles, deprecation contract, manifest structure, credential-redaction guidance and audit-method catalog.
- The lab project initially had `deploymentmanager.googleapis.com` disabled, but it remains an eligible existing customer: after propagation, enabling the API and creating a deployment still succeeded. The API was restored to disabled after each fixture.
- Read-only inspection confirmed the project Google APIs Service Agent still has project `roles/editor`. The current Editor definition contains `compute.instances.create`, `compute.instances.setServiceAccount`, and `iam.serviceAccounts.actAs`.
- Live testing used a synthetic bucket deployment and a temporary service account to resolve deployment-level IAM scope. Every deployment and bucket was deleted, each direct deployment policy was restored before deletion, every temporary account was deleted, and the API was restored to disabled. Final bucket/account/API checks found no residue. No VM, network or privileged target credential was created.

## Retained privilege escalation

### `deploymentmanager.deployments.create` / `.update`

Status: retained and consolidated into one deputy-execution technique.

Evidence and bounds:

- Google documents that Deployment Manager calls downstream services as `PROJECT_NUMBER@cloudservices.gserviceaccount.com` and grants that principal Editor by default.
- The V2 API authorizes insert with `deploymentmanager.deployments.create` and update with `deploymentmanager.deployments.update`; both are Admin Activity LROs.
- The default Editor grant can create a Compute VM and satisfy `iam.serviceAccounts.actAs` for a same-project service account. A controlled VM can then use that attached account through the metadata server. This can exceed the deputy's own Editor privileges when the selected service account is more privileged.
- Raw insert needs only `.create`; raw update can use `.update` plus a known fingerprint. Local inspection of the current Google Cloud CLI found that the `gcloud` create helper always calls `deployments.get` after insert to print a fingerprint. Thus `.create` alone can trigger the insert, but the helper then exits with an error if that read is denied. The update helper calls `deployments.get` before and after update even when `--fingerprint` is supplied. `--async` avoids operation polling and final resource/manifest rendering, but not these deployment reads.
- Synchronous helper execution additionally calls `operations.get`, `resources.list`, and `manifests.get` when a manifest exists. These helper permissions are not part of the raw API minimum.
- The chain fails or narrows when the service agent's roles were hardened, the selected account is outside its `actAs` scope, downstream APIs/quota/networking are unavailable, or organization and IAM policies block the downstream action.
- Cross-project attachment has additional boundaries: the account project must allow it, the relevant service agent or agents need Service Account Token Creator on the account, and the Google APIs Service Agent still needs `actAs`. Same-project attachment does not require those cross-project settings.
- Service-account attachment produces a separate always-on `iam.serviceAccounts.actAs` Admin Activity entry under the Google APIs Service Agent, in addition to the Compute insert entry.
- Repository history already contained live evidence that downstream resource creation was attributed to the Google APIs Service Agent and direct project IAM replacement failed while the agent held Editor. This iteration reconfirmed V2 insert/delete LRO start/completion behavior with a zero-data Cloud Storage bucket but did not recreate the billable VM fixture.

### `deploymentmanager.deployments.setIamPolicy`

Status: retained after live minimum-scope validation.

- Created an empty-policy deployment and bound `roles/deploymentmanager.admin` directly on that deployment to a temporary service account that had no project role.
- The API accepted the binding, and an access token for that service account immediately retrieved the exact deployment with HTTP 200. This proves the predefined Admin role is effective at the deployment despite the role catalog not printing a lowest-level-resource line for it.
- The generic `testIamPermissions` call returned 403 because it separately required project-level `deploymentmanager.deployments.list`; it is not a valid negative test for a deployment-only grant.
- Admin contains `.update`, so the direct binding reaches the deputy-execution primitive for that existing deployment. It does not make project-level `.create` applicable or affect another deployment.
- The policy write emitted non-LRO Admin Activity method `v2.deploymentmanager.deployments.setIamPolicy`. Policy/deployment reads are off-default Data Access. The binding was removed before deleting the deployment.

## Reclassified post-exploitation

### `deploymentmanager.manifests.get`

Status: moved to a dedicated post-exploitation page.

- A known manifest needs only `.get`; `.deployments.list` and `.manifests.list` are discovery aids.
- The manifest retains original configuration/imports, expanded configuration and layout for every update. Google's credential guidance confirms that template imports and YAML key/value or list shapes can preserve unredacted credentials.
- Corrected the old blanket claim that all manifest secrets are cleartext: some credential-property keys are redacted, and template credentials are redacted from expanded config/layout but remain in the original import.
- All relevant list/get methods are non-LRO Data Access `ADMIN_READ`, disabled by default.

## Rejected as standalone techniques

### Type-provider descriptor retrieval

Status: research lead only.

- The control plane can fetch a caller-selected descriptor URL, but documentation does not establish useful internal reachability, response disclosure or credential forwarding.
- If a controlled test demonstrates cross-boundary server-side request behavior, keep it private as a potential platform vulnerability until triaged.

### Template expansion as code execution

Status: rejected.

- Google documents configuration expansion in a controlled environment. Python/Jinja template authoring is not a documented project workload or a supported arbitrary-execution primitive.

## 2026-09-28 — independent cross-review

- Rechecked the deprecation dates, V2 REST IAM schema, audit catalog, live deployment-level IAM evidence, current predefined-role metadata, manifest/redaction contract, and local gcloud source.
- Corrected the gcloud helper minimums, cross-project service-account boundary, separate `actAs` audit signal, policy-member visibility, and the overbroad wording that implied arbitrary execution as the Google APIs Service Agent.
- The deployment-level `roles/deploymentmanager.admin` result is retained as live evidence for the named deployment. No claim is made that it grants project-level create authority.
- No cloud API or resource mutation was performed during this independent review.
