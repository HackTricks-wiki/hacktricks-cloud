# CloudWatch Logs scheduled-query role-mediated exfiltration — 2026-09-26

## Result

Verified end to end in account `228478051196`, `us-east-1`:

- A disposable log group contained one random marker.
- A query role could query only that group; a separate delivery role could write only one prefix in a disposable S3 bucket. Both trusted `logs.amazonaws.com`.
- The restricted positive caller held only `logs:CreateScheduledQuery` plus `iam:PassRole` on those exact two roles, conditioned with `iam:PassedToService = logs.amazonaws.com`. It had no direct log-read or S3-write action.
- An enabled one-minute scheduled query reached `Complete`, delivered one JSON object, and the object contained the exact marker.

This is expected AWS functionality, not a vulnerability. Cross-account S3 delivery is officially supported but was not exercised because only one authorized account was confirmed.

## Two independent PassRole gates

The service checks the destination role first:

1. Caller with `logs:CreateScheduledQuery` and no PassRole: denied on `iam:PassRole` for the S3 delivery role.
2. Caller with PassRole only on the delivery role: advanced and was denied on `iam:PassRole` for the query execution role.
3. Caller with PassRole on both exact roles: creation succeeded.

The documented service condition worked for both roles:

```json
"Condition": {
  "StringEquals": {
    "iam:PassedToService": "logs.amazonaws.com"
  }
}
```

## CloudTrail evidence

- Successful and denied `CreateScheduledQuery` calls appeared in ordinary Event History.
- The successful event had `managementEvent: true`, `eventCategory: Management`, and resource type `AWS::Logs::ScheduledQuery`.
- `requestParameters` contained the complete query string, log-group list, cron expression, offsets, state, execution-role ARN, S3 URI, bucket-owner account ID, and delivery-role ARN.
- Automatic `StartQuery` appeared as a default management event under `assumed-role/<query-role>/Logs`, with `invokedBy: logs.amazonaws.com`; it repeated the query text and target group.
- Automatic `GetQueryResults` appeared under the same role/session pattern and contained the query ID.
- Destination `PutObject` is an S3 object data event and was not present in Event History without an object data-event selector.
- `iam:PassRole` produced no standalone event.

This live result overrides an easy misreading of the generic CloudTrail resource-type list: scheduled-query creation is a management event by default in this service implementation.

## API/model notes

- AWS CLI `2.34.45` supports the S3 destination but not newer `endTimeOffset` or lookup-table destination fields.
- boto3/botocore `1.43.99` supports both newer fields.
- `cron(* * * * ? *)` was accepted and fired at the next minute boundary; AWS's public examples describe 15 minutes as high frequency but do not document a hard 15-minute minimum.
- History reported `Complete`, a query ID, the processed S3 object URI, and destination status `COMPLETE`.
- The S3 result was a JSON array of selected rows and contained no `@ptr` or query statistics.

## Cleanup

The schedule was deleted before the data plane. Final independent checks showed:

- no matching scheduled query
- bucket returned HTTP 404 after its result object was removed
- log group absent
- all three IAM users/keys/policies `NoSuchEntity`
- both roles/policies `NoSuchEntity`

No persistent residue remains.

## Follow-ups

- Verify `UpdateScheduledQuery` can repoint an existing schedule with the same two PassRole gates; documented very likely, not needed for the primary creation technique.
- Exercise documented cross-account S3 delivery only if a second account is explicitly authorized.
- Test lookup-table destinations separately with the newer SDK; assess whether their destination role creates a distinct data-poisoning path.
