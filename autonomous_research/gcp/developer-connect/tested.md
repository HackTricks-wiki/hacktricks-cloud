# Developer Connect research ledger

## 2026-09-28 documentation and local-source audit

Scope was documentation/read-only only. No API was enabled, no Developer Connect resource or external provider installation was created, and no token method was invoked.

### Evidence inspected

- Current official Developer Connect v1 REST reference, audit-log catalog, proxy guide, account-connector model, Insights overview, IAM roles page, and GCP-2026-048 security bulletin.
- Current local `gcloud developer-connect` GA help for connections, repository links, `fetch-read-token`, `fetch-read-write-token`, account connectors, Insights configs, and deployment events.
- Current generated v1 client/message sources in the installed Google Cloud CLI for paths, verbs, request/response schemas, and account-connector user semantics.
- Current predefined-role descriptions via read-only `gcloud iam roles describe`.

### Verified role and API boundaries

| Surface | Verified result |
| --- | --- |
| Raw repository read token | `FetchReadToken` requires `developerconnect.gitRepositoryLinks.fetchReadToken`; Beta `readTokenAccessor` and `tokenAccessor` contain it. Response contains `token`, `gitUsername`, and `expirationTime`. The stable contract says it fetches the token of the named link and does not document reusable authority outside that repository. |
| Raw repository read/write token | `FetchReadWriteToken` requires `developerconnect.gitRepositoryLinks.fetchReadWriteToken`; Beta `tokenAccessor` contains it. GA Developer Connect Admin does not. |
| System Git proxy | GA `gitProxyReader` contains `gitProxyRead`; GA `gitProxyUser` and Developer Connect Admin contain `gitProxyRead` + `gitProxyWrite`. Proxy must be enabled and provider controls still apply. |
| Account connector token | `POST .../accountConnectors/{id}/users:fetchAccessToken` has an empty request and no user selector. Official description says it is based on end-user credentials. OAuth Admin and OAuth User contain the permission, but neither can use this RPC to select another linked `User`. |
| Account connector proxy | OAuth User/Admin contain account-connector `gitProxyRead`/`gitProxyWrite`; access is tied to the caller's linked provider user and selected OAuth scopes. |
| Generic HTTP connection | Preview connections can reference a Secret Manager-backed bearer/basic credential and expose an output-only HTTP proxy base URI. Beta `connectionHttpProxyWriter` contains `connections.httpProxyRead`/`httpProxyWrite`, but no supported end-user invocation or audit contract is currently documented. |
| Developer Connect service agent | `roles/developerconnect.serviceAgent` contains connection/link gets and connection HTTP-proxy permissions, but neither raw token fetch permission. |
| Other product service agents | Cloud Build and Firebase App Hosting service-agent roles currently contain read/write token fetch; additional product roles contain read token fetch. Official IAM guidance says not to grant service-agent roles to ordinary principals. |
| Insights | GA Insights Viewer/Admin roles are separate; CLI viewers also need Container Analysis Occurrences Viewer on the host project per the setup guide. Configs can target projects distinct from the config-owning project, but the Developer Connect P4SA must separately receive the GA Insights Agent role on target projects/folder. Deployment relationships are reconnaissance, not authority over targets. |

### Audit-contract results

- `google.cloud.developerconnect.v1.DeveloperConnect.FetchReadToken`: Data Access, permission type `DATA_READ`, non-LRO, off by default.
- `google.cloud.developerconnect.v1.DeveloperConnect.FetchReadWriteToken`: Data Access, permission type `DATA_READ`, non-LRO, off by default.
- `GetGitRepositoryLink`: Data Access/`ADMIN_READ`, non-LRO, off by default.
- Connection/link writes and Insights config writes listed in the catalog are Admin Activity/`ADMIN_WRITE` LROs and logged by default; related `GetOperation` is Data Access/`ADMIN_READ`, off by default.
- The current official audit catalog does not list account-connector/user RPCs or Git/HTTP proxy traffic. Their Cloud Audit Logs method names/classes/default visibility were deliberately left as an explicit documentation gap instead of inferred.

### Retained techniques

1. Post-exploitation: export a linked repository read credential with `fetchReadToken`.
2. Post-exploitation: export the named link's provider write credential with `fetchReadWriteToken`; no broader provider scope is claimed without evidence.
3. Post-exploitation: read or write a linked system repository through an enabled Git proxy without exporting the provider credential.
4. Post-exploitation: recover the compromised caller's own previously linked provider OAuth access token with `users:fetchAccessToken`, strictly bounded to that user/scopes.
5. Conditional privilege escalation: use `fetchReadWriteToken` or Git-proxy write to alter a repository ref/file consumed automatically by a more-privileged build/deployment identity.

### Rejected or corrected hypotheses

- **Developer Connect Admin can mint raw Git tokens:** false. The current GA role lacks both fetch permissions, although it can use the system Git proxy.
- **OAuth Admin can steal any listed user's provider token:** false for the current RPC. The path/body contain no user selector and the server chooses the user from end-user credentials.
- **Repository write automatically equals pipeline-SA execution:** false. Developer Connect does not execute source. A writable consumed ref, an automatic downstream trigger, and a more-privileged execution identity are all required; provider protections remain effective.
- **Insights config/deployment-event access is escalation:** rejected as reconnaissance without a separate authorization crossing.
- **Connection CRUD alone exfiltrates caller-selected cross-project secrets:** rejected for the current service. GCP-2026-048 records that both caller and P4SA secret access are now checked for GitLab Enterprise and Bitbucket Data Center connections.
- **Account-connector creation/update is durable service-level persistence:** rejected. It still needs an end user/provider OAuth authorization for useful access and is readily enumerated/revoked; generic project IAM persistence is documented elsewhere.
- **OAuth Admin can silently add scopes to existing user grants:** false. Current documentation says a scope update removes all existing users, who must authorize again.
- **`generateGitHubStateToken` or OAuth `startOAuthFlow` returns a reusable provider credential:** rejected. These support browser authorization state/PKCE/ticket flows; the current credential-returning RPCs are `fetchReadToken`, `fetchReadWriteToken`, and self-scoped `fetchAccessToken`.
- **Generic HTTP proxy is already a reproducible credential-broker technique:** not yet supported. The current Preview resource/permissions prove the capability exists, but official docs do not publish an end-user request protocol and it was not live-tested in this read-only pass.
- **Git proxy/account-connector token calls are definitely unlogged:** unsupported. Their methods are missing from the published catalog, which is a telemetry-contract gap, not evidence that runtime logs never exist.

### Files produced by this audit

- Rewrote the Developer Connect privilege-escalation page to one bounded conditional chain.
- Added Developer Connect enumeration and post-exploitation pages and SUMMARY entries.
- Did not add a persistence page because no distinct, high-value service-level primitive survived review.

## 2026-09-28 independent cross-review

- Reconfirmed from current predefined-role metadata that GA Developer Connect Admin includes system Git-proxy read/write but excludes both raw-token fetch permissions. The Beta Token Accessor roles are the raw-token boundary; the Beta OAuth User/Admin roles remain the self-scoped account- connector boundary even though the account-connector service is now GA.
- Removed the unsupported claim that a token fetched for one `gitRepositoryLink` can necessarily be reused across every repository visible to an installation or stored PAT. The stable API promises a read or read/write token for the named link and does not publish its concrete provider type or authority outside that repository.
- Corrected Git examples to avoid embedding provider/Google tokens in the remote URL and process arguments. The system-proxy workflow now uses Google's documented `gcloud.sh` credential helper; the raw-token workflow uses an ephemeral Git helper backed by exported shell variables.
- Bounded Git-proxy writes to the documented `roles/developerconnect.gitProxyUser` workflow, whose role contains both `gitProxyRead` and `gitProxyWrite`. Public documentation does not establish a supported `gitProxyWrite`-only workflow.
- Tightened the CI/CD escalation chain: the exact external repository/ref/event must be watched, the provider must permit that ref update, required approvals must not block it, and the triggered execution identity must exceed the caller's authority. Developer Connect itself executes no code.
- Rechecked GCP-2026-048 against the product bulletin and release notes. For GitLab Enterprise and Bitbucket Data Center connection secrets, both caller and P4SA now need `secretmanager.versions.access`; this statement is not generalized to unrelated Preview generic HTTP-connection secret fields.
- Reconfirmed exact audit treatment: raw `FetchReadToken`/`FetchReadWriteToken` are non-LRO, off-default `DATA_READ`; `GetGitRepositoryLink` is off-default `ADMIN_READ`; account-connector and Git-proxy methods remain absent from both the audited and explicit no-audit lists, so visibility is documented as unknown rather than no-log.
- All four post-exploitation techniques and the single conditional privilege-escalation chain clear the usefulness bar after these bounds. No extra CRUD, destructive-only, or persistence heading was added, and no cloud/provider operation was performed.
