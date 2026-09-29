# Recommender — tested

## 2026-09-29 — live nine-tool MCP surface and IAM recommendation intelligence

- The unauthenticated live `https://recommender.googleapis.com/mcp` schema exposed nine tools: four
  list/get tools and five recommendation/insight state-mutation tools. The current static MCP
  overview lists only the four reads. Anonymous execution remained rejected.
- A disposable IAM Recommender Viewer returned three existing IAM recommendations directly and
  through the MCP transport. Results named over-privileged default service accounts, their Editor
  grants, proposed replacement roles, exact IAM-policy patch operations and security projections
  exceeding 12,000 revoked permissions. No recommendation content was copied into research files.
- A caller without the type-specific update permission was denied on
  `recommender.iamPolicyRecommendations.update`. After that expected product permission propagated,
  a state tool against an impossible synthetic recommendation UUID reached the backend and returned
  `Requested entity was not found`; no real recommendation or insight was targeted or mutated.
- Default logging produced no Recommender or MCP caller record, matching the documented exclusion
  of list/get and all five state-marking methods from Cloud Audit Logs.
- All three existing IAM recommendations remained ACTIVE after testing. Removed the disposable
  Viewer/Admin/quota-project grants, key, service account and isolated gcloud configuration;
  Recommender remained enabled at its original baseline and exact residue checks were empty.

## Retained public techniques

- Precomputed privilege/attack-path intelligence from recommendations and insights.
- Unlogged workflow-state defense evasion through recommendation dismissal/false completion and
  insight acceptance, bounded to Recommender state rather than the underlying resource.
