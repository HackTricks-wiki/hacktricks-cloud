# App Service Domains — Candidate Attacks (not yet lab-fired)

- [ ] If an explicitly disposable, transfer-eligible App Service Domain becomes available, assign a
      `domains/*` role with all published mutations excluded and verify that `transferOut` returns only
      that domain's EPP code. Do not buy or transfer a domain solely for this test; never use a shared or
      production registration.
- [ ] Enumerate built-in and custom roles whose action wildcards match the hidden
      `Microsoft.DomainRegistration/domains/transferOut/write` operation. Prioritize misleading
      service-scoped roles; Contributor/Owner are already expected matches.
- [ ] Recheck each new DomainRegistration API/provider-operation version for an explicit assignable
      `transferOut/write` operation. If Microsoft publishes it, update the book's minimum permission and
      remove the wildcard-only caveat.
