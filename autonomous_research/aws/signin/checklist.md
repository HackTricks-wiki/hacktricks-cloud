# AWS Sign-In next checks

- [x] Verify policy and enforcement are separate operations.
- [x] Check account baseline and create/delete a disabled statement with full teardown.
- [ ] In a dedicated disposable account, test allowed and denied fresh sign-ins with a known recovery principal and full teardown.
- [x] After CloudTrail ingestion, confirm configuration event source, category, and Region; both writes were management events in `us-east-1`.
- [ ] Inspect request fields only when needed for a concrete detection question.
- [ ] Review Sign-In RCP permissions and organization-wide scope for a separate high-value path.
- [ ] Test IAM Identity Center portal behavior only in a dedicated disposable account.
