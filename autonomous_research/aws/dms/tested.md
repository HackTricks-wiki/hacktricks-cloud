# DMS — tested

## 2026-09-26 authorization and credential-coercion audit

### Exact-resource `ModifyEndpoint` — worked

- Created a disposable MySQL source endpoint containing a synthetic username/password.
- A disposable IAM user holding only `dms:ModifyEndpoint` on the exact generated endpoint ARN successfully changed the top-level server name and port. It had no DMS describe action and no `iam:PassRole`.
- The username and other omitted settings remained present after the partial update. `DescribeEndpoints` exposed neither the top-level password nor a nested password field.
- This supports the existing endpoint-redirection boundary and the book now states its exact minimum permission and prerequisites.

### Stored Redis-token coercion through `TestConnection` — inconclusive; not shipped

Hypothesis: create a plaintext Redis target endpoint with a synthetic authentication token, change only its `RedisSettings.ServerName`/port through exact-resource `ModifyEndpoint`, and invoke `TestConnection` so a listener can verify whether DMS retains and transmits the omitted token.

The safe end-to-end fixture used:

- one `t3.micro` EC2 listener in the default VPC;
- an isolated listener/client security-group pair;
- the required DMS VPC role and replication subnet group; and
- one DMS replication instance.

The first launch was rejected before creating a replication resource because `dms.t3.micro` is no longer an orderable DMS class in `us-east-1`. The current orderable inventory showed `dms.t3.small` as the smallest supported class. A retry with `dms.t3.small` remained in `creating` for the test's ten-minute readiness cap, so the script deleted it without ever creating the Redis endpoint or invoking `TestConnection`.

Disposition: do not publish credential capture. The API contract and Redis plaintext-auth design make it a reasonable future test, but endpoint setting retention plus actual authentication transmission was not demonstrated end to end in this pass. Keep it in the research queue rather than presenting it as confirmed.

### Cleanup and cost

Both endpoint-only fixtures were deleted after their calls; DMS endpoint deletion was asynchronous and was polled until absent. The full fixture cleanup deleted the EC2 listener, DMS replication instance, subnet group, both security groups, instance profile, temporary IAM users/roles/policies/access keys, and the conditionally created `dms-vpc-role`.

An independent final inventory returned zero resources with the `ht-audit-dms-` or `ht-dms-` prefixes across EC2 instances, DMS instances/endpoints/subnet groups, security groups, IAM users, roles, and instance profiles. No real secret or source database was used. The short-lived EC2 and DMS instances remained far below the authorized cost ceiling.

## NEGATIVE — `dms:DescribeEndpoints` does NOT disclose stored endpoint passwords
- **Hypothesis (historical claim):** DescribeEndpoints leaks the endpoint DB `Password` in cleartext.
- **Tested live (2026-09-25, acct 228478051196, us-east-1):** created a mysql source endpoint with
  `--password`, then DescribeEndpoints. Response returns `Username`, `ServerName`, `Port`,
  `MySQLSettings.AuthenticationMethod=password` — but **no password value**. The top-level
  `Endpoint.Password` member has been **removed from the output shape entirely** (botocore: Endpoint
  output has `Username` but no `Password`); nested engine-settings passwords are likewise not returned.
  `grep` for the plaintext password = NO match. Endpoint deleted (async), verified deleting→gone.
- **Conclusion:** AWS has closed this historical disclosure. NOT a technique. The DMS enum page already
  covers the still-valid angle (endpoint-repoint / role abuse). Not shipped.
- **Calibration:** confirms the AppStream finding — the "Describe returns a stored password" lens is
  dead across AWS. [[appstream]]
