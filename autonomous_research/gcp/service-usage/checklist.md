# Service Usage research checklist

## Completed 2026-09-28

- [x] Separate API enablement from target-service authorization.
- [x] Separate quota-project use from principal authentication and target-service IAM.
- [x] Reclassify service disablement as defense evasion/availability impact.
- [x] Reclassify consumer quota override changes as availability/cost abuse rather than privilege escalation.
- [x] Redirect API key creation and secret access to the dedicated API Keys attack surface.
- [x] Record current authorization-key service-account role and organization-policy prerequisites.
- [x] Correct Service Usage and API Keys audit classes and LRO behavior.
- [x] Review Preview hierarchical consumer policies and the deprecated MCP enablement policy.
- [x] Inspect the v2beta MCP content-security schema and live read-only behavior; record that the
      current endpoint returns `SU_MCP_DEPRECATED` and says the policy has no effect.

## Independent cross-review completed 2026-09-28

- [x] Reconfirm that no retained Service Usage operation independently grants target-service IAM or
      changes the caller's principal identity.
- [x] Add the private-service `servicemanagement.services.bind` enablement boundary.
- [x] Split raw consumer-policy `.update` from the default gcloud helper's additional `.analyze`
      call (skipped by `--bypass-dependency-check`) and distinguish unlogged analysis/GET methods
      from the Admin Activity update LRO.
- [x] Split Service Usage override LRO telemetry from non-LRO Cloud Quotas preference telemetry.
- [x] Recheck standard API-key versus authorization-key role, service-account, organization, and
      managed-constraint boundaries.
- [x] Independently reproduce both `SU_MCP_DEPRECATED` policy GET failures and the working consumer-
      policy GET without printing policy contents or changing state.

## Open bounded leads

- [ ] Recheck newly added Service Usage consumer-policy or MCP-policy fields for an actual
      authorization expansion, not merely enablement, restriction, or quota configuration.
- [ ] If Google adds another API that supports authorization keys, verify the exact service-account
      binding permissions and org-policy allowlist before expanding the API Keys technique.
- [ ] Test disable/reenable telemetry and service-agent lifecycle only as a reversible defensive
      experiment in a disposable project; do not present service-agent creation as escalation unless
      a caller can actually obtain or use the agent's authority without an independent impersonation
      permission.
