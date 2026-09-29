# Cloud Support — tested

## 2026-09-29 — support-case reads and remote MCP boundary

- Anonymous discovery exposed six read-only MCP tools: case search/get, comment list/get, and
  attachment list/get. The MCP attachment object is metadata only; the direct v2 media method is
  the separate byte-download surface.
- Enabled the API from its disabled baseline and used a disposable Tech Support Viewer. Direct
  empty-query search succeeded with an empty result, while the same identity without
  `mcp.tools.call` was denied specifically at the MCP gate. An Owner positive control returned the
  same empty result through MCP; anonymous invocation returned HTTP 401.
- A conditional MCP Tool User binding allowing only `search_cases` permitted that tool while a
  `get_case` call remained denied despite the underlying Viewer role, confirming exact tool-name
  control for this server after IAM propagation.
- The official audit catalog explicitly excludes stable v2/v2beta `SearchCases` from Cloud Audit
  Logs. Known-resource case/comment/attachment reads are off-default `DATA_READ`; no test-principal
  entry appeared under the default configuration.
- No case, comment, or attachment was created, changed, downloaded, or deleted. Removed the key,
  service account, every binding, both conditional grants, and local credentials; disabled the API
  back to baseline and verified zero residue.
