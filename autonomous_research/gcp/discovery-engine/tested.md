# Discovery Engine / Gemini Enterprise — tested

## 2026-09-28 — BigQuery connector authorization-boundary review

- Confirmed from current official documentation that one-time BigQuery ingestion can support source
  access control, while periodic ingestion explicitly does not. Google warns that BigQuery IAM is
  not imported and Gemini Enterprise users with sufficient access can view the indexed copy without
  permission on the source table.
- Classified this as an expected post-exploitation data-exposure path, not a BigQuery IAM bypass:
  an administrator must already have connected the sensitive table and exposed the resulting
  application or data store to the attacker.
- Confirmed `SearchService.Search` requires `discoveryengine.servingConfigs.search`, is categorized
  as `DATA_READ`, and produces Data Access logs only when that log class is enabled. No cloud
  resource was created during this documentation-only review.
- Cross-review bounded the impact to indexed documents and retrievable fields in the last successful
  copy; this is not arbitrary live-table access and does not remove the source BigQuery policies.
  Periodic ingestion is Preview and refreshes every one, three or five days.
- The audit-log reference guarantees the method, class and permission but not preservation of the
  request's query text. Detection guidance therefore relies on principal, serving configuration and
  volume unless representative logs establish more fields for a deployment.
