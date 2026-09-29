# Application Design Center — tested

## 2026-09-29 — Viewer cross-service Storage reach and MCP boundaries

- The live `https://designcenter.googleapis.com/mcp` endpoint anonymously exposed six tools:
  `manage_application`, `manage_application_template`, `assess_best_practices`, `setup_adc`,
  `list_application_templates` and `manage_catalog`. Every current schema advertised
  `readOnlyHint=false`, including the list tool. Anonymous invocation returned HTTP 401.
- A disposable service account with only MCP Tool User and Service Usage Consumer passed the MCP
  wrapper after propagation but received the expected backend denial for
  `designcenter.applicationTemplates.list`. This cleanly separated `mcp.tools.call` from backend
  Design Center authorization; no MCP bypass was found.
- Adding only project-level `roles/designcenter.viewer` made
  `designcenter.applicationTemplates.list`, `storage.objects.list` and `storage.objects.get`
  effective in project IAM tests. `storage.buckets.list/get` remained absent. The caller still
  could not use the Design Center read because the project was deliberately not configured as the
  management project/app-enabled-folder scope, a product-hierarchy limitation rather than an IAM
  discrepancy.
- Despite Design Center being unconfigured, the Viewer successfully enumerated a synthetic object
  in a known project bucket and downloaded its exact marker. The same identity's project bucket
  listing was denied on `storage.buckets.list`, proving the known-bucket boundary.
- Official role inspection also found broad compliance/audit reads and `container.clusters.list` in
  Viewer; User adds template/component/connection mutations and broad Storage object/folder writes.
  Application roles retain separate downstream deployment and service-account prerequisites.
- The project had no `auditConfigs`. The successful Storage object list/get and denied Design
  Center/MCP reads produced no matching caller audit record, consistent with their Data Access
  classifications. The three project IAM grants produced always-on `SetIamPolicy` Admin Activity.
- Retained one high-value expected post-exploitation technique: use an existing Design Center Viewer
  binding to read objects from known buckets, with normal folder inheritance potentially widening
  scope. This is predefined-role authority, not a vulnerability or MCP authorization bypass.
- Deleted the synthetic object and bucket, removed Viewer/MCP/Service Usage grants, deleted the key
  and service account, disabled the Design Center API back to baseline, and trashed every isolated
  config/schema/response file. No Design Center space/setup, service identity or App Hub state was
  created. Exact IAM, identity, bucket, API and `/tmp` residue checks were empty.
