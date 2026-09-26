# AWS Support App in Slack checklist

## Completed

- [x] Inspect the current AWS CLI service model for create/update inputs, required IDs, role ARN, and
  notification controls.
- [x] Confirm from the Service Authorization Reference that create/update use `Resource: "*"` and
  depend on `iam:PassRole` with `iam:PassedToService = supportapp.amazonaws.com`.
- [x] Enumerate existing Slack workspace/channel configurations and Support App-trusting roles.
- [x] Verify the lab has no premium Support API entitlement and therefore no safe live fixture.
- [x] Enumerate the exact current `AWSSupportAppFullAccess` and `AWSSupportAppReadOnlyAccess` policy
  actions.
- [x] Confirm the documented Slack command surface is Support cases and Service Quotas, not arbitrary
  AWS API execution.
- [x] Validate the CloudTrail management-event shape from the earlier bounded nonexistent-ID update.
- [x] Record zero mutations and zero cleanup residue for this review.

## Revisit only with an existing authorized fixture

- [ ] Use a test-owned Slack workspace/channel that is already authorized and a premium Support plan;
  do not onboard a third-party workspace merely for this test.
- [ ] Bind an isolated describe-only channel role and prove a distinct Slack-only user can retrieve a
  synthetic canary support case that the AWS configuration principal cannot read directly.
- [ ] Verify individual Slack-user attribution across Support case correspondence, CloudTrail Support
  API events, and Slack audit logs.
- [ ] Test update from a read-only to a write-capable support role, then rollback to the original role.
- [ ] Delete the channel configuration and test role/policy; if authorization was test-only, have the
  workspace owner remove the app/OAuth authorization and independently verify both inventories.
