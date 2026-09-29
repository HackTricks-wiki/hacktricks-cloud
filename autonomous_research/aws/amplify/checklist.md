# AWS Amplify — open ideas

- [x] UpdateApp env-var/buildSpec RCE as existing role — already documented (pre-existing page).
- [x] UpdateBranch environment-variable RCE as the existing service role — live verified with an
  exact-branch restricted caller, a dormant Node startup hook, and a one-way canary hash. Published;
  see tested.md. Direct branch `buildSpec` replacement was stored but ignored by the build and is
  recorded as a negative boundary rather than a technique.
- [x] UpdateApp role-repoint privesc (iamServiceRoleArn/computeRoleArn + PassRole) — DONE, authz
  VERIFIED. See tested.md.
- [x] amplify:GetApp/ListApps/GetBranch env-var disclosure + amplifybackend token minting — documented.
- [ ] **CreateDomainAssociation / webhook (CreateWebhook)** persistence — a webhook URL that triggers
  builds is a credential-less remote build trigger; combined with a poisoned buildSpec it re-executes
  attacker code on demand. Check webhook auth model + whether it survives IAM principal removal.
- [ ] **CreateBranch --enable-auto-build --build-spec** on a repo-connected app — a new branch with a
  malicious buildSpec that auto-builds on push = persistence. Needs a connected repo to test.
