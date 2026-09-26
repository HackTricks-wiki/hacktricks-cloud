# AWS Sign-In next checks

- [x] Verify policy and enforcement are separate operations.
- [x] Check account baseline and create/delete a disabled statement with full teardown.
- [ ] In a dedicated disposable account, test allowed and denied fresh sign-ins with a known recovery principal and full teardown.
- [ ] After CloudTrail ingestion, inspect actual configuration event source and request fields.
- [ ] Review Sign-In RCP permissions and organization-wide scope for a separate high-value path.
- [ ] Test IAM Identity Center portal behavior only in a dedicated disposable account.
