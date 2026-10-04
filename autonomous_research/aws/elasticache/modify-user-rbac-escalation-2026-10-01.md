# ElastiCache exact-user RBAC escalation audit — 2026-10-01

## Result

Verified and published the missing privilege-escalation consequence of
`elasticache:ModifyUser`. A restricted IAM user authorized only for one exact ElastiCache user ARN
simultaneously:

- replaced an attacker-unknown password with a caller-chosen password; and
- changed a disabled, narrow ACL into `on ~* +@all`.

The caller could not invoke `DescribeUsers`. It had no user-group, cache, Secrets Manager, KMS,
IAM PassRole, service-linked-role, network, or other ElastiCache permission. Administrator inventory
observed the user return to `active` with the unrestricted access string, password authentication,
and one configured password.

On a production Valkey/Redis OSS cache, the resulting impact is conditional on the target user
already belonging to the cache's attached user group and on the attacker having the user name,
endpoint, port, and network reachability. No cache was created for this control-plane test, so the
research does not claim a live data-plane connection. AWS's RBAC model and `ModifyUser` contract
establish that the widened ACL controls the user's key and command permissions.

## Exact authorization boundary

The live IAM user had only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "elasticache:ModifyUser",
      "Resource": "arn:aws:elasticache:us-east-1:228478051196:user:ht-ec-rbac-20261001045123"
    }
  ]
}
```

Its `DescribeUsers` control returned `AccessDenied`. The accepted mutation was semantically:

```bash
aws elasticache modify-user \
  --user-id ht-ec-rbac-20261001045123 \
  --access-string 'on ~* +@all' \
  --authentication-mode 'Type=password,Passwords=[REDACTED]'
```

No password or access-key value was printed or retained. The response returned `Status=modifying`,
the unrestricted access string, password authentication, and `PasswordCount=1`. After convergence,
an administrator read returned:

```json
{
  "Status": "active",
  "AccessString": "on ~* +@all",
  "AuthType": "password",
  "PasswordCount": 1
}
```

## Safe fixture

- Region: `us-east-1`
- ElastiCache user ID/name: `ht-ec-rbac-20261001045123`
- Engine: Redis OSS
- Initial ACL as canonicalized by the service: `off ~restricted:* -@all +get +ping`
- Initial and replacement authentication: one generated password each
- User groups/caches: none
- Restricted IAM user: same run ID

The absence of a user group deliberately prevented authentication to any cache. No cache nodes,
serverless cache, VPC resource, ENI, snapshot, S3 object, KMS key, secret, role, or billable workload
was created.

## CloudTrail evidence

- Event time: `2026-10-01T04:51:40Z`
- Event name/source: `ModifyUser` / `elasticache.amazonaws.com`
- Event ID: `bcb53141-fffe-4df9-90e1-7a352ccc56c2`
- Request ID: `46859c46-85fc-49c9-89c2-341caf85a5e3`
- `readOnly:false`
- `managementEvent:true`

After the initial ingestion delay, Event History showed that the request records the exact `userId`,
`accessString:"on ~* +@all"`, authentication type, and a password array whose value is
`HIDDEN_DUE_TO_SECURITY_REASONS`. The response records the canonical access string, `modifying`
status, password authentication/count, and exact user ARN. The event's top-level `resources` field
was null, so detections should parse request/response fields rather than depending on that array.

The denied `DescribeUsers` control was also a default management event (`eventID`
`60f7d748-be52-4a67-a957-b2ecc0da1b8e`) with `errorCode:AccessDenied`; its request parameters were
null. Engine-level `AUTH` and data commands would not be ElastiCache API calls and therefore would
not appear in CloudTrail.

## Cleanup

The restricted IAM access key, inline policy, and user were deleted. ElastiCache user deletion is
asynchronous; the first immediate check observed it still present during deletion, and a subsequent
independent poll confirmed actual absence. Creating the first ElastiCache RBAC user had also
auto-created `AWSServiceRoleForElastiCache`; CloudTrail exposed that side effect, so the role was
explicitly deleted and independent `GetRole`/`ListRoles` checks confirmed absence:

```text
final_elasticache=[] final_iam=[] final_slr=[]
```

There is no cost or cleanup debt.

## Disposition

- Expected service behavior with a high-impact permission composition: published as cache
  data-plane privilege escalation.
- No unexpected AWS malfunction was observed and no private vulnerability report was opened.
