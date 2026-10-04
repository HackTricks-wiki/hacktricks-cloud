# ElastiCache CreateUserGroup authorization audit — 2026-10-01

## Result

Verified the exact prospective-resource minimum for `elasticache:CreateUserGroup`:

- allowing only the exact future group ARN was denied on the initial `default` user ARN;
- allowing the exact future group plus both initial user ARNs created the group;
- an otherwise authorized second future group containing an ungranted outsider was denied on that
  outsider-user ARN; and
- `DescribeUserGroups` remained denied.

The accepted group reached `active` with exactly the default and intended member. It was not attached
to a cache, so no data-plane access changed.

## CloudTrail evidence

The successful default management write:

- event time: `2026-10-01T05:55:33Z`
- event ID: `987572fd-807e-4074-8452-63c89d195900`
- request ID: `eb8edc8d-cee8-4f98-92cd-8f6c2902dc48`
- `readOnly:false`, `managementEvent:true`

The request and response both retained the prospective group ID, Redis engine, and complete initial
user-ID list. The response also included the exact group ARN and `status:"creating"`; top-level
`resources` was null.

The group-only denial was event `2625a516-7cc3-4380-a4f9-0ef434edfcd7`; the outsider denial was
`038319fa-c3ec-4501-99c2-cba59a52ac8b`. Their request/response/resource fields were null, while
`errorMessage` named the missing exact user ARN.

## Cleanup and disposition

The group, all three RBAC users, restricted access key/policy/IAM user, and auto-created ElastiCache
SLR were deleted. Final inventories returned:

```text
final_groups=[] final_users=[] final_iam=[] final_slr=[]
```

Expected and correctly scoped AWS behavior. The existing persistence technique was corrected; no
private report and no cleanup debt.
