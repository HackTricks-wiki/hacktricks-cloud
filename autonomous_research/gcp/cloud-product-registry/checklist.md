# Cloud Product Registry — open leads

- [x] Map GA REST and remote MCP methods, unauthenticated behavior, documented IAM model, and MCP
  tool annotations.
- [x] Reject unauthenticated `tools/list` as an attack: it returns only public schemas and does not
  execute catalog reads.
- [ ] Re-run REST and MCP calls after the GA rollout stabilizes, using a consumer project for which
  a normal OAuth caller or API key successfully lists suites. Compare an underlying-only identity
  against `roles/mcp.toolUser`; keep any missing `mcp.tools.call` enforcement private-first.
- [ ] Diff lifecycle-state output against public launch records. Only investigate privately if the
  registry exposes genuinely non-public products, private identifiers, or confidential launch
  timing; deprecated and `PRIVATE_GA` enum values alone are not vulnerabilities.
- [ ] Fuzz `lookupEntity` path decoding, type confusion, pagination tokens, and suite filters using
  documented public identifiers. Stop at public catalog data; never treat ordinary product names
  as victim reconnaissance.
