# Account Access Manager — next checks

- [ ] On a permitted organization management/delegated-admin lab with Account Access Manager already enabled, verify `CreateEntitlement` with a policy granting only that action on the application ARN; check positive assignment and negative without the action. The current lab has Identity Center in `eu-west-1` but `ListApplications` returns `[]`.
- [ ] Test the role-trust boundary with a prepared low-privilege role and a non-trusting role. Confirm the latter cannot issue a role session.
- [ ] Capture sanitized `CreateEntitlement`, `DeleteEntitlement`, and portal role-assumption CloudTrail events; confirm the exact `eventSource`, event category, region, and principal/role fields.
- [ ] Remove every test entitlement immediately and verify `ListEntitlements` no longer returns it. Do not create a new organization Identity Center instance solely for this test.
- [ ] Audit whether `DeleteEntitlement` can remove a break-glass workforce assignment and how promptly existing role sessions expire; keep this in research until impact is established.
