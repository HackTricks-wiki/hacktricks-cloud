# Access Context Manager — open ideas

Open ideas — Access Context Manager / VPC-SC.

- [x] Reconcile Preview Workforce extended sessions: ship the 90-day Looker-scoped persistence
      path, all-pools/single-binding restriction, background-refresh prerequisites, 24-hour
      staleness kill switch, exact ACM roles, and Admin Activity methods.
- [ ] In an authorized disposable organization with Looker core and WIF, compare new versus existing
      sessions, append versus replace, OIDC refresh-token versus SCIM refresh, IdP revocation timing,
      Looker application-session limits, and exact request payloads. Restore the binding/provider.
- [ ] Private-first: test whether restricted-project scope, one-binding enforcement, attribute
      staleness, or provider/pool separation can be bypassed. Never use a production IdP identity.
- The `replaceAll`×2 → `policies.delete` teardown chain is ALREADY documented in `gcp-privilege-escalation/gcp-access-context-manager-privesc.md` (bulk-overwrite section, with min perms, audit method names and teardown angle). Verified duplicate → not re-tested, nothing to ship.
