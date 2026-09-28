# Agent Registry security research checklist

## Completed — 2026-09-29

- [x] Map v1/v1alpha resources, mutable fields, stable URNs, locations and role contents.
- [x] Enumerate Services, Agents, MCP Servers, Endpoints and Bindings with the current CLI/API.
- [x] Verify the minimum predefined-role path for Service-interface mutation.
- [x] Confirm target URN, projected resource name and auth Binding survive URL replacement.
- [x] Confirm current ADK combines the replacement MCP URL with the original auth-provider scheme
      without transmitting the credential.
- [x] Capture the UpdateService LRO audit shape and map read/retrieval Data Access events.
- [x] Delete every Service, Binding, provider, account, key, grant, local dependency and API change.

## Private-first validation frontier

- [ ] Create two source Agents and two synthetic auth providers bound to the same MCP target. Prove
      whether ADK ignores the source identifier and chooses the first target match. Use distinct
      non-secret marker keys, provider-scoped runtime grants and an in-process receiver only.
- [ ] Repeat the two-source test with reversed creation order and pagination to determine whether
      provider selection is deterministic or unstable.
- [ ] Test the equivalent target collision for `get_remote_a2a_agent()` and Endpoint consumers.
- [ ] Verify whether the API intends to allow plain source-to-target Bindings without an auth
      provider; the live v1 service currently rejects them despite product documentation.
- [ ] Enable Agent Registry Data Access temporarily around a synthetic run to capture exact request
      redaction for Service reads, projected-resource reads and Binding lists. Restore the original
      audit policy byte-for-byte.

## Do not publish without stronger evidence

- [ ] No claim that Service update immediately returns a credential; victim retrieval and
      invocation are required.
- [ ] No claim that every runtime honors Registry Bindings; the verified consumer is current ADK's
      MCP toolset helper.
- [ ] No claim that gateway/egress policy, hostname validation or audience enforcement cannot block
      the redirected request.
- [ ] Keep any cross-source auth-provider confusion private until reproduced end to end with two
      isolated principals and synthetic credentials.
