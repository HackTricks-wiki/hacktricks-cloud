# Personalized Service Health security research

## 2026-09-29 — project-footprint inference and remote MCP surface

- Mapped the two read-only project-event tools at `https://servicehealth.googleapis.com/mcp`. Unauthenticated `tools/list` returned the complete schemas; anonymous invocation returned 401.
- Retained one post-exploitation technique because event relevance leaks materially useful project context: `RELATED` connects an affected product and location to the project, while `PARTIALLY_RELATED` confirms product use. Full view also returns diagnosis, symptoms, workarounds and every incident update.
- A narrow custom caller with only `servicehealth.events.list`, quota/project context and the MCP wrapper permission retrieved 60 historical events and 375 update records through direct REST and MCP. The same caller was independently denied `servicehealth.events.get` through both transports.
- The MCP setup guide currently lists only `mcp.tools.call` in its required-permissions section, but the live server correctly enforced the underlying `servicehealth.events.list/get` permission. No authorization bypass was found.
- Direct and wrapper calls produced no caller entry under the default audit configuration, matching the documented off-default Data Access classification. Service-generated incident update logs are separate from read audit telemetry.
- Deleted the disposable identity, key, custom role, all bindings, local gcloud configuration and response artifacts; restored the Service Health API to its disabled baseline. Exact residue checks found no active test principal, binding, config, API or local credential.
