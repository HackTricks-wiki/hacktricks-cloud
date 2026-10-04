# ElastiCache ModifyUserGroup authorization audit — 2026-10-01

## Result

Verified that `elasticache:ModifyUserGroup` authorizes both the target user group and every user
named in the add/remove lists. This corrects the minimum permissions for the existing RBAC
persistence technique:

- action allowed only on the exact group ARN: denied on the added-user ARN;
- action allowed on the exact group, added user, and removed user: accepted;
- same policy attempting to add a different outsider user: denied on the outsider-user ARN; and
- `DescribeUserGroups` remained denied throughout.

After the accepted asynchronous mutation returned to `active`, administrator inventory showed the
default user and attacker user in the group; the victim user was absent. No cache used the group, so
the test changed no live data-plane access.

## Exact successful boundary

The successful policy was semantically:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "elasticache:ModifyUserGroup",
    "Resource": [
      "arn:aws:elasticache:us-east-1:228478051196:usergroup:ht-ecgroup-20261001054240-group",
      "arn:aws:elasticache:us-east-1:228478051196:user:ht-ecgroup-20261001054240-attacker",
      "arn:aws:elasticache:us-east-1:228478051196:user:ht-ecgroup-20261001054240-victim"
    ]
  }]
}
```

## CloudTrail evidence

The successful `ModifyUserGroup` event:

- event time: `2026-10-01T05:44:15Z`
- event ID: `e4ea81f1-6a09-43d1-aeb1-46be3d4f64f6`
- request ID: `bad1711c-0822-4bd0-a186-d7a3030b662d`
- `readOnly:false`, `managementEvent:true`

The request retained the group ID and exact add/remove user-ID lists. The response recorded the
previous membership plus `pendingChanges.userIdsToAdd`/`userIdsToRemove`; top-level `resources` was
null.

The group-only denial was event `ec09b790-4d28-4313-ad2d-6565637c8879`; the outsider-user denial was
`a1279a3b-87c0-4e1c-bfe6-2019dd5911c4`. Both IAM-denied events had null request/response/resource
fields, but `errorMessage` named the exact missing user ARN. The denied Describe control was also a
default management event.

## Cleanup and disposition

The group, four RBAC users, restricted access key/policy/IAM user, and auto-created ElastiCache SLR
were deleted. Independent final inventories returned:

```text
final_groups=[] final_users=[] final_iam=[] final_slr=[]
```

Expected and correctly scoped AWS behavior. The public persistence page was corrected; no private
report was opened and there is no cost or cleanup debt.
