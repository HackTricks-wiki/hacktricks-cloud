# Dialogflow CX — open research

- [x] Reconcile webhook create/update/detectIntent with the current Data Access audit contract.
- [x] Bound retained-header/OAuth-secret redirection to existing routing and service-agent access.
- [x] Split configured-service-account OAuth token capture into Dialogflow privilege escalation and
      add the new page to the book summary.
- [x] Reject audience-bound service-agent ID-token capture as a general reusable credential.
- [ ] In a disposable agent with synthetic secrets, test field-masked URI and OAuth-token-endpoint
      updates under a minimum custom role; capture Data Access and runtime logs, restore the exact
      webhook, then delete the agent, secret, receiver data and temporary grants.
- [ ] In the same disposable fixture, configure a least-privileged synthetic service account and
      test a URI-only update first without and then with `iam.serviceAccounts.actAs`. Determine
      whether Dialogflow rechecks an unchanged `serviceAccountAuthConfig`, capture any
      `GenerateAccessToken` record, revoke the receiver data/token, and restore every binding.
- [ ] Test whether a supported Service Directory webhook can be redirected across endpoint/project
      boundaries without a matching authorization change. Keep a genuine boundary failure private
      and restore/delete every endpoint and namespace immediately.
