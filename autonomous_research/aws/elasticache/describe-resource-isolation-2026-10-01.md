# ElastiCache Describe resource-isolation audit — 2026-10-01

## Result

Verified that resource-scoped `DescribeUsers` and `DescribeUserGroups` fail closed rather than
leaking unrelated objects:

- policy allowed `DescribeUsers` only on user A's exact ARN;
- policy allowed `DescribeUserGroups` only on group A's exact ARN;
- filtered A calls succeeded and returned only A;
- filtered B calls were denied on B's exact ARN; and
- unfiltered calls were denied on `arn:aws:elasticache:us-east-1:228478051196:user:*` and
  `...:usergroup:*` rather than returning a silently filtered inventory.

This establishes a useful least-privilege boundary: exact-resource readers must know the identifier
and use the corresponding request filter; account inventory requires wildcard resource permission.

## Fixture

The free control-plane fixture used three Redis users (one `default`, A, and B), two unattached user
groups, and one restricted IAM user. Groups A and B shared the default user and each included its
corresponding test user. No cache, subnet, endpoint, snapshot, object, data, or traffic existed.

## Cleanup and disposition

Both groups, all three RBAC users, the restricted access key/policy/IAM user, and the auto-created
ElastiCache SLR were deleted. The first list caught the SLR during asynchronous deletion; polling the
exact deletion task returned `SUCCEEDED`, and final inventory confirmed:

```text
final_groups=[] final_users=[] final_iam=[] final_slr=[]
```

Expected/correctly isolated behavior. The enumeration page was clarified; no private report and no
cleanup debt.
