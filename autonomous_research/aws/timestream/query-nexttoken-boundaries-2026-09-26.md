# Timestream Query NextToken boundaries — deferred 2026-09-26

## Hypothesis

The Timestream Query API documents unusually strong pagination-token properties worth regression
testing:

- the query initiator and result reader must be the same IAM principal;
- both requests must use the same query string;
- one `NextToken` is valid for at most five invocations or one hour;
- replay returns the same page; and
- using a newer child token invalidates its older parent.

Potential security failures include a token disclosing rows to a different/no-Select principal,
cross-query use reaching another table, result delivery after an observable explicit IAM deny, or a
racing replay counter allowing more than five uses. Token mutation, wrong-Region use, failure not
consuming the owner's token, and same-role/different-STS-session identity semantics should accompany
the core cases.

## Intended minimum fixture

- One disposable database and two tables, six tiny marker rows each, `MaxRows=1`.
- Owner role: `timestream:DescribeEndpoints` plus `timestream:Select` on table A.
- Second session of owner, peer role with identical table-A permission, and endpoint-only denied role.
- Fixed 32-character `ClientToken` per chain, SDK retries disabled, raw query/token/page values hashed.
- Hard caps: 40 Query calls, 100 MB reported cumulative metering, one six-worker race, no Query Insights.
- Cleanup: delete both tables/database and all temporary role policies/roles in `finally`.

## Preflight result

Not testable in the authorized account. Both `timestream-write ListDatabases` and
`timestream-query DescribeEndpoints` in `us-east-1` returned:

```text
AccessDeniedException: Only existing Timestream for LiveAnalytics customers can access the service.
Reach out to AWS support, for more information.
```

AWS closed LiveAnalytics access to new customers on 2025-06-20 while allowing existing customers to
continue. No database, table, IAM role, or other fixture was created. Do not try to bootstrap or
bypass this account-level gate. Revisit only in an explicitly authorized existing-customer payer.

## Sources

- <https://docs.aws.amazon.com/timestream/latest/APIReference/API_query_Query.html>
- <https://docs.aws.amazon.com/timestream/latest/developerguide/AmazonTimestreamForLiveAnalytics-availability-change.html>
- <https://aws.amazon.com/timestream/pricing/>
