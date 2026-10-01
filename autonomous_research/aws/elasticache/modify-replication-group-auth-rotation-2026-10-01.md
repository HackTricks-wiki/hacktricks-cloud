# ElastiCache legacy AUTH rotation audit — 2026-10-01

## Result

Verified and published a low-disruption legacy AUTH credential-takeover path. An IAM user with only
`elasticache:ModifyReplicationGroup` on one exact replication-group ARN supplied a caller-chosen
token and `AuthTokenUpdateStrategy=ROTATE`. The caller could not describe the group and had no
cache-cluster, RBAC user/group, Secrets Manager/KMS, EC2, Lambda, IAM, or PassRole permission.

After the group returned to `available`, two isolated Lambda connections from the same VPC/security
group established TLS and spoke the Redis protocol directly. The original token and the
caller-chosen token independently returned successful `AUTH` and `PONG`. This proves that `ROTATE`
adds an attacker credential without immediately revoking the legitimate credential.

## Exact authorization boundary

The live restricted user had only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "elasticache:ModifyReplicationGroup",
      "Resource": "arn:aws:elasticache:us-east-1:228478051196:replicationgroup:ht-ecauth-20261001045911"
    }
  ]
}
```

Its `DescribeReplicationGroups` control returned `AccessDenied`. The accepted mutation was
semantically:

```bash
aws elasticache modify-replication-group \
  --replication-group-id ht-ecauth-20261001045911 \
  --auth-token REDACTED \
  --auth-token-update-strategy ROTATE \
  --apply-immediately
```

No token or access-key value was printed or retained.

## End-to-end controls

The disposable replication group used Redis OSS, one `cache.t4g.micro` node, TLS, legacy AUTH, the
default VPC and its default security group. No application key/value was written. A test-only Lambda
function joined the same security group and used a minimal TLS/RESP client; it received each
synthetic token only in its invocation payload and returned only status flags:

```text
initial_token_result={"auth":"ok","ping":"ok"}
attacker_token_result={"auth":"ok","ping":"ok"}
```

The probe role had only AWS's managed Lambda VPC-ENI policy. It was an administrator-side validation
fixture, not a permission attributed to the restricted attacker.

## CloudTrail evidence

- Event time: `2026-10-01T05:04:34Z`
- Event name/source: `ModifyReplicationGroup` / `elasticache.amazonaws.com`
- Event ID: `9090dbf2-c8a4-4fd2-9121-ee9c80c5e150`
- Request ID: `2a071d5c-4b0a-479a-bc9c-27e5523feb1b`
- `readOnly:false`
- `managementEvent:true`

Event History recorded `replicationGroupId`, `applyImmediately:true`,
`authTokenUpdateStrategy:"ROTATE"`, and `authToken:"HIDDEN_DUE_TO_SECURITY_REASONS"`. The response
recorded the exact group ARN, member cluster, endpoint/port, TLS mode, `status:"modifying"`, and
`pendingModifiedValues.authTokenStatus:"ROTATING"`. The top-level `resources` field was null, so
detections should parse request/response fields rather than depend on the resource array.

## Cleanup

The Lambda function, Lambda role, restricted access key/policy/user, cache node, replication group,
and auto-created `AWSServiceRoleForElastiCache` were deleted. The cache node disappeared inside the
authorized 30-minute/cost window. Lambda left four detached, `available`, non-requester-managed ENIs;
each was exact-description matched and explicitly deleted:

```text
eni-02538d86296d71bee
eni-0a1b5c183634d94bd
eni-02a345cf194cfb00e
eni-02570629d1b59ecb2
```

An independent final inventory confirmed all test-owned resources absent:

```text
final_rg=[] cache_clusters=[] enis=[] functions=[] users=[] roles=[]
```

There is no cost or cleanup debt.

## Disposition

- Expected AWS feature composition: publish as data-plane access/service-level persistence.
- No unexpected malfunction was observed and no private report was opened.
