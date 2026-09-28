# Developer Connect research checklist

## Completed

- [x] Compare Developer Connect Admin with read-token, read/write-token, proxy, OAuth, Insights, and service-agent predefined roles and record current launch stages.
- [x] Verify GA CLI syntax and v1 REST paths for connections, repository links, raw token fetch, account connectors, users, Insights configs, and deployment events.
- [x] Separate raw-token authorization from Git-proxy authorization.
- [x] Confirm `users:fetchAccessToken` is selected by end-user credentials and exposes no arbitrary `User` selector.
- [x] Bound repository-write escalation by provider write authority, branch/ref controls, a downstream trigger, and the downstream execution identity.
- [x] Check official audit classes/default visibility and preserve explicit catalog gaps.
- [x] Reassess cross-project Secret Manager selection after GCP-2026-048.
- [x] Inventory generic HTTP connection/proxy permissions and keep them out of the book as an unreproduced Preview surface.
- [x] Reject Insights, OAuth administration, connection CRUD, and generic IAM grants as distinct service-level privilege-escalation/persistence primitives.
- [x] Independently re-check raw-token accessor roles versus GA Admin Git-proxy permissions.
- [x] Bound fetched provider credentials to the named link unless broader provider authority is separately evidenced and authorized.
- [x] Replace credential-bearing Git URLs with helper-based clone/push examples and validate Bash syntax.
- [x] Reconfirm the self-selected `users:fetchAccessToken` path and audit-catalog omission.
- [x] Reconfirm GCP-2026-048 caller-plus-P4SA `secretmanager.versions.access` checks only for the named GitLab Enterprise/Bitbucket Data Center path.

## Safe future validation

- [ ] In a disposable provider repository, call `fetchReadToken` with only the Beta Read Token Accessor role and verify clone succeeds but push fails; capture the exact provider token type, expiry, provider audit event, and enabled Developer Connect Data Access log.
- [ ] Repeat `fetchReadWriteToken` with only the Beta Token Accessor role; verify unprotected-branch push versus protected-branch denial on the named link and identify the concrete provider token type. Do not probe other repositories unless separately authorized.
- [ ] With an enabled system proxy, test `gitProxyReader` versus `gitProxyUser` using a known URI and capture any Cloud Logging entry/resource/method not yet present in the public audit catalog.
- [ ] Link two distinct end users to one disposable account connector. Verify OAuth Admin plus `users.list` cannot make `users:fetchAccessToken` return the other user's token, and record `lastTokenRequestTime` behavior.
- [ ] Capture account-connector `fetchAccessToken`, `fetchSelf`, `fetchUserRepositories`, Git proxy, and HTTP proxy runtime telemetry to resolve the current audit-catalog gap.
- [ ] In a disposable endpoint/secret setup, derive the generic HTTP proxy request protocol, test `connectionHttpProxyWriter` alone, bound path/header forwarding, and capture proxy/provider telemetry.
- [ ] Test whether current generic HTTP connection create/update applies caller-and-P4SA authorization to a cross-project Secret Manager credential. Treat this only as a hypothesis until safely reproduced; GCP-2026-048 explicitly documents the fix for GitLab Enterprise and Bitbucket Data Center, not this newer Preview config.
- [ ] Test a cross-project consumer service account granted a narrow token/proxy role in the connection-owning project and confirm the effective IAM resource boundary and any VPC Service Controls behavior.
- [ ] Verify current double authorization for a disposable cross-project GitLab Enterprise/Bitbucket Data Center secret reference using separately controlled caller and P4SA grants; do not create a real connection unless provider and cleanup are available.
- [ ] Re-check the role/audit catalog after the Beta token/OAuth roles reach GA or their permissions change.

## Cleanup requirements for any future live test

- Remove all test IAM bindings from both connection and consumer projects.
- Delete repository links, connections/account connectors, test Insights configs, generated secrets, webhooks, provider installations/OAuth grants, pushed refs, and CI/CD triggers.
- Revoke minted/provider OAuth tokens where supported and confirm long-running deletions completed.
- Restore APIs and audit-log settings to their pre-test state.
