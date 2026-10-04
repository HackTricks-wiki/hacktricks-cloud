# Discovery Engine / Gemini Enterprise — tested

## 2026-09-29 — granular app and data-store IAM review

- Confirmed the new resource-level model independently checks the target app (`engine`) and linked data store. Restricted users require a narrow project-level persona plus a resource-level Agentspace User, Viewer, or Admin grant on both resources.
- Confirmed project-level Agentspace predefined roles override the intended resource isolation. Third-party connectors with entities additionally require the collection and every child entity data store; REST does not cascade the collection policy, while the console does.
- Mapped `engines.setIamPolicy`, `dataStores.setIamPolicy`, and `collections.setIamPolicy` as scoped privilege-escalation and service-level-persistence primitives when isolated in custom or conditional roles. Full predefined Agentspace/Discovery Engine admins already hold the resulting authority, so this is not extra escalation for those roles.
- Confirmed `SetIamPolicy` is always-on Admin Activity (`ADMIN_WRITE`); policy reads are Data Access (`ADMIN_READ`). Added missing impact, permission, stealth, and log metadata to both existing Discovery Engine persistence techniques.
- The lab's Discovery Engine API was disabled and no app or data store existed. Kept the review to current official contracts rather than enabling/provisioning a licensed service solely for a test; the read-only probes created no cloud state.

## 2026-09-28 — BigQuery connector authorization-boundary review

- Confirmed from current official documentation that one-time BigQuery ingestion can support source access control, while periodic ingestion explicitly does not. Google warns that BigQuery IAM is not imported and Gemini Enterprise users with sufficient access can view the indexed copy without permission on the source table.
- Classified this as an expected post-exploitation data-exposure path, not a BigQuery IAM bypass:
  an administrator must already have connected the sensitive table and exposed the resulting application or data store to the attacker.
- Confirmed `SearchService.Search` requires `discoveryengine.servingConfigs.search`, is categorized as `DATA_READ`, and produces Data Access logs only when that log class is enabled. No cloud resource was created during this documentation-only review.
- Cross-review bounded the impact to indexed documents and retrievable fields in the last successful copy; this is not arbitrary live-table access and does not remove the source BigQuery policies. Periodic ingestion is Preview and refreshes every one, three or five days.
- The audit-log reference guarantees the method, class and permission but not preservation of the request's query text. Detection guidance therefore relies on principal, serving configuration and volume unless representative logs establish more fields for a deployment.
