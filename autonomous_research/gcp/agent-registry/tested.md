# Agent Registry security research ledger

## 2026-09-29 — service-interface redirect across a stable auth binding

- Reviewed stable v1 discovery revision `20260916`, v1alpha, Google Cloud SDK 586.0.0 help,
  official concepts/setup/binding/authentication/roles/audit documentation and all four predefined
  `roles/agentregistry.*` roles.
- Mapped Services as the writable manual-registration layer and Agents/MCP Servers/Endpoints as
  projected discovery resources. A Binding stores source and target URNs plus an Agent Identity
  auth provider, while the mutable target URL remains in `Service.interfaces`.
- Live-created a synthetic source Agent Service, target MCP Service, API-key provider and Binding in
  `us-central1`. An isolated caller with only `roles/agentregistry.editor` and
  `roles/serviceusage.serviceUsageConsumer` changed the target URL. It had no Binding-write or
  Agent Identity provider-update authority.
- The Service retained the same `registryResource`; the projected MCP server retained the same
  resource name and `mcpServerId`; and the Binding retained its source, target and auth provider.
  The projected MCP object exposed the replacement URL but its `updateTime` remained at the
  pre-update value.
- Installed the current Google ADK only in a disposable local virtual environment. Its
  `get_mcp_toolset()` resolved a toolset containing both the replacement URL and the unchanged
  `GcpAuthProviderScheme`. No credential was transmitted to any host. Official ADK/auth-manager
  documentation and implementation establish that invocation retrieves and injects the provider
  credential.
- The UpdateService LRO emitted two always-on Admin Activity records identifying the isolated
  caller and target Service. Registry gets/lists are `ADMIN_READ` Data Access, off by default;
  Agent Identity credential retrieval is `DATA_READ`, also off by default.
- A project-level Agent Registry Editor grant did not become usable until the caller also received
  `serviceusage.services.use`, confirming the quota-project prerequisite. Binding creation rejected
  a request without an auth provider even though current product prose also describes plain
  resource-connection bindings; retained as a contract discrepancy, not a separate attack.
- Cleanup deleted the Binding, two regional and two initial global Service fixtures, synthetic auth
  provider, temporary service account/key/config, IAM grants and local ADK environment. Agent
  Registry, Agent Identity, Agent Identity Credentials and the automatically enabled App Hub API
  were restored to their disabled baseline. No test asset or IAM reference remains.

## Private-first follow-up

- The current ADK binding resolver receives no source-agent identifier and matches only the target
  URN while iterating all Bindings. Test two source agents bound to the same target with different
  auth providers. If one source receives the other's provider and can use its credential, treat it
  as a private vulnerability report rather than a public expected-functionality technique.
- Test whether duplicate target bindings are rejected, deterministically ordered or returned in an
  unstable order. Capture only synthetic credential markers and never send a real token externally.
- Compare MCP, A2A-agent and generic Endpoint helper behavior. The published book entry is bounded
  to the verified MCP toolset path.
