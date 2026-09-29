# Semantic Governance — tested

Last reviewed: 2026-09-29.

## Retained expected technique

- Semantic Governance policies are the natural-language enforcement layer for an Agent Registry agent's tool calls and skill invocations. The policy object can scope a constraint to the whole agent or selected MCP servers/tools.
- `aiplatform.semanticGovernancePolicies.update` can replace the natural-language constraint and change the `agent` or `mcpTools` scope. `aiplatform.semanticGovernancePolicies.delete` removes the policy. Either can remove a guardrail that would otherwise deny a proposed action.
- This is defense evasion, not privilege escalation: the target agent still needs its original MCP and downstream-service authorization. The policy mutation neither grants IAM permissions nor bypasses a tool server's own authentication/authorization.
- Current `roles/aiplatform.user`, `roles/aiplatform.editor`, and `roles/aiplatform.admin` all carry policy create/delete/get/list/update. The unexpectedly broad User-role inclusion makes this worth a book entry.

## Live authorization and audit evidence

The project already had `aiplatform.googleapis.com` enabled. Its regional Semantic Governance engine was `INACTIVE` and no policy existed, so the test used only nonexistent resource names and did not provision the engine or create a policy.

- An authenticated v1 `PATCH` against a nonexistent policy passed IAM and returned `NOT_FOUND`. It emitted an always-on `cloudaudit.googleapis.com/activity` entry with:
  - method `google.cloud.aiplatform.v1.SemanticGovernancePolicyService.UpdateSemanticGovernancePolicy`;
  - permission `aiplatform.semanticGovernancePolicies.update`;
  - permission type `ADMIN_WRITE`.
- An authenticated v1 `DELETE` against the same nonexistent policy passed IAM and returned `NOT_FOUND`. It emitted Admin Activity with method `google.cloud.aiplatform.v1.SemanticGovernancePolicyService.DeleteSemanticGovernancePolicy`, permission `aiplatform.semanticGovernancePolicies.delete`, and permission type `ADMIN_WRITE`.
- A disposable principal with no project role received `PERMISSION_DENIED` on the same delete. Its Admin Activity entry used the same method and exact denied permission, confirming the gate independently of predefined-role inspection.
- Installed Cloud SDK 586.0.0 exposes stable `gcloud ai semantic-governance-policies` create, delete, describe, list and update commands and stable engine describe/update/deprovision commands. Update accepts `agent`, `mcp-tools`, `natural-language-constraint`, and an optional concurrency `etag`.

## Engine-deprovision permission discrepancy

The documented deprovision RPC is not authorized by the published engine `.update` permission:

- separate update-only and get-only principals both received `PERMISSION_DENIED` on an `INACTIVE` engine before any state transition;
- both audit entries checked the exact backend permission `aiplatform.semanticGovernancePolicyEngine.deprovision` and used `google.cloud.aiplatform.v1.SemanticGovernancePolicyEngineService.DeprovisionSemanticGovernancePolicyEngine`;
- `gcloud iam list-testable-permissions` currently returns only engine `.get` and `.update`;
- `roles/aiplatform.user`, `.editor`, `.admin`, and basic Owner all omit `.deprovision`, as does the public role/permission reference.

The operationally checked permission is therefore currently unpublished and not catalog-grantable. This is an administrative product-contract defect, not an attacker primitive, and is not included in the book. Do not suggest `.update` or Owner can deprovision until the catalog changes. Do not force-deprovision an active fixture merely to retest it.

## Visibility and documentation boundaries

- Policy update/delete are confirmed Admin Activity even though the current general Agent Platform audit-method catalog has not yet added Semantic Governance rows.
- Runtime evaluations use the `semantic-governance-policy` log and built-in `aiplatform.googleapis.com/semantic_governance/*` metrics. These help detect vanished evaluations or verdict shifts but are not the configuration audit record.
- Current documentation conflicts on VPC Service Controls: the policies overview still says the feature is unsupported, while broader Agent Gateway/Agent Platform material documents VPC-SC support when current VPC connectivity requirements are met. The book does not make an absolute claim until feature-specific documentation converges.

## Cleanup

- Removed both engine-permission probe bindings, deleted both service accounts and custom roles, deleted their cloud keys, shredded both local key files, and deleted the isolated gcloud configs.
- Removed the no-role delete-probe account and cloud key, shredded its local key/token material, and deleted its isolated config.
- Verified no matching service account, active project binding, active custom role, key, or local config remained. The engine stayed `INACTIVE`; no policy or other service resource was created.
- The Vertex AI API remained enabled because it was enabled before testing.

