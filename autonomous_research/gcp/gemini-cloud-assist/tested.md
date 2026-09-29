# Gemini Cloud Assist — tested

## 2026-09-29 — MCP surface, investigation records and predefined-role Storage reach

- The unauthenticated live `https://geminicloudassist.googleapis.com/mcp` schema exposed six tools:
  `ask_cloud_assist`, `investigate_issue`, `optimize_costs`, `invoke_operation`, `design_infra` and
  `ask_cloud_operator`. The schemas span broad estate/log/source/cost reconnaissance and confirmed
  GKE, design and operational mutations. Anonymous execution was rejected.
- A custom caller with `geminicloudassist.agents.invoke`, project read and quota consumption was
  denied at the separate `mcp.tools.call` wrapper. Adding MCP Tool User reached the wrapper after
  propagation. Adding Gemini Cloud Assist User also reached the product backend, but both that
  caller and the Owner control received the same embedded permission failure. The project lacks the
  service's Private Preview entitlement, so agent execution/downstream authorization is not treated
  as validated and no bypass is claimed.
- Current predefined-role inspection found that `roles/geminicloudassist.user` directly grants
  `storage.objects.list/get`, folder and managed-folder reads, broad App Design Center artifact
  mutations and App Hub application mutations. A disposable principal with only that project-level
  role successfully listed and downloaded a synthetic marker from a known bucket through the
  Storage JSON API. It had no Storage role. The role lacks bucket list/get, bounding discovery to a
  bucket name learned elsewhere.
- The synthetic Storage list/get produced no caller audit record under the project's default audit
  configuration; the Owner's bucket create/delete appeared in always-on Storage Admin Activity.
  This validates the book's off-default Data Access distinction without claiming universal silence.
- The current project contained no investigation fixture. Official current schemas establish that
  investigations retain operational observations and that revision resources preserve historical
  snapshots. All investigation/revision get/list methods are Data Access `ADMIN_READ`, disabled by
  default. This source-backed technique was retained without manufacturing sensitive content.
- Retained two public techniques: harvest investigation/revision history, and use the direct
  Storage object permissions bundled into Gemini Cloud Assist User. The role's design-artifact
  writes remain enumeration context rather than a weak standalone attack.
- Removed the role bindings, custom role, service account, key, isolated gcloud configuration,
  synthetic object/bucket and schema/response files. Soft-deleted the custom role and restored
  `geminicloudassist`, Design Center, App Hub and App Optimize APIs to their disabled baseline;
  Cloud Asset remained enabled at baseline. Exact identity, binding, bucket, API and local-artifact
  residue checks were empty.
