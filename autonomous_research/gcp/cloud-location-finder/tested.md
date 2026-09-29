# Cloud Location Finder — tested/rejected

## 2026-09-29 — generic public catalog, no retained attack

- The live `https://cloudlocationfinder.googleapis.com/mcp` schema exposes two read-only tools:
  `list_cloud_locations` and `search_cloud_locations`. Anonymous tool execution is rejected.
- Official documentation defines the product as a public, daily refreshed repository of Google
  Cloud, Google Distributed Cloud, AWS, Azure and OCI public locations. Returned fields are generic
  provider/region/zone, territory, nesting, proximity and carbon-free-energy metadata rather than
  victim project resources or deployments.
- Current v1 discovery exposes only get/list/search. Although the role catalog contains create,
  update and delete permission names, there are no corresponding current v1 methods or MCP tools;
  do not infer a location-poisoning primitive from permission names alone.
- No authenticated call, API enablement, identity or resource was needed. The surface was rejected
  from the book because it does not provide victim-specific reconnaissance, a foothold, privilege
  gain, persistence or meaningful defense evasion.
