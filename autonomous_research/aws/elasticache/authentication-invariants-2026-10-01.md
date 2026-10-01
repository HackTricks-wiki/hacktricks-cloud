# ElastiCache authentication invariant audit — 2026-10-01

## Result

Two free control-plane security hypotheses failed safely under live exact-user authorization:

1. A Redis OSS user with `no-password-required` could not be transitioned to Valkey, either with
   `Engine=valkey` alone or with an explicit simultaneous no-password authentication mode.
2. A password user whose `UserId` and `UserName` differed could not be transitioned to IAM
   authentication.

The restricted caller had only `elasticache:ModifyUser` on the two exact user ARNs and could not
call `DescribeUsers`. Administrator reads after all attempts returned the original Redis engine and
authentication modes unchanged. Neither user belonged to a group or cache.

## Service responses and CloudTrail

All three writes returned `InvalidParameterCombinationException`:

| Attempt | Event ID | Service error |
| --- | --- | --- |
| Redis no-password user, `Engine=valkey` | `6a0bdd0e-38d6-4e90-bbb7-1f910b01c698` | `No-password-required is not allowed for a user with engine Valkey` |
| Same transition with explicit no-password mode | `c4109cbd-ad4b-4088-83c3-7c299addb76e` | `No-password-required is not allowed for a user with engine Valkey` |
| Mismatched ID/name user, `AuthenticationMode=iam` | `c4aec5dc-27ef-4f34-9d5b-829dad5aea9c` | `User Id and User name must be same for authentication type: iam` |

The failed default management events retained the target user ID and attempted engine/authentication
mode, returned no response elements, and exposed the validation reason. No password value was part
of these mutation attempts.

## Cleanup and disposition

Both ElastiCache users, the restricted access key/policy/IAM user, and the auto-created
`AWSServiceRoleForElastiCache` were deleted. Final inventories were:

```text
final_elasticache=[] final_iam=[] final_slr=[]
```

The hypotheses are closed as correctly enforced validation, not AWS vulnerabilities. No public
attack technique or private report was added. There is no cost or cleanup debt.
