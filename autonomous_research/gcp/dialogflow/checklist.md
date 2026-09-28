# Dialogflow CX — open research

- [x] Reconcile webhook create/update/detectIntent with the current Data Access audit contract.
- [x] Bound retained-header/OAuth-secret redirection to existing routing and service-agent access.
- [x] Live-test configured-service-account auth and remove the provisional privilege-escalation page:
      arbitrary external and Cloud Run URLs are rejected, and a Google-API URI-only update still
      requires `iam.serviceAccounts.actAs` on the retained account.
- [x] Reject audience-bound service-agent ID-token capture as a general reusable credential.
- [ ] In a disposable agent with synthetic external secrets, test field-masked URI and OAuth-token-endpoint
      updates under a minimum custom role; capture Data Access and runtime logs, restore the exact
      webhook, then delete the agent, secret, receiver data and temporary grants.
- [x] In a disposable fixture, configure a zero-role synthetic service account and test a Google-API
      URI-only update first without and then with `iam.serviceAccounts.actAs`. The first request was
      denied and the control succeeded; arbitrary external and Cloud Run receivers were rejected.
- [ ] Test whether a supported Service Directory webhook can be redirected across endpoint/project
      boundaries without a matching authorization change. Keep a genuine boundary failure private
      and restore/delete every endpoint and namespace immediately.
