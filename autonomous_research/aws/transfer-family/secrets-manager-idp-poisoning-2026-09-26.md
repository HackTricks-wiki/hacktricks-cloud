# Transfer Family Secrets Manager custom-IdP record poisoning — 2026-09-26

## Outcome

Verified end to end that `secretsmanager:PutSecretValue` on one exact legacy custom-IdP user secret
can replace both its credential and Transfer authorization response. A restricted caller that could
not read the record, pass a role, mutate Transfer/Lambda/API Gateway, or access S3 wrote a complete
replacement version. A real password-authenticated SFTP session then read an object exposed only by
the injected Transfer role.

This is expected composition of the published template and Secrets Manager version semantics, not an
AWS vulnerability. It was added to the public Transfer privesc page. The newer custom-IdP toolkit
stores authorization attributes in DynamoDB, so secret-only poisoning does not select a new role in
that architecture; a DynamoDB record-poisoning test remains open.

## Fixture

- Region/account: `us-east-1`, authorized account `228478051196`.
- Disposable public SFTP server using an IAM-protected API Gateway route and Lambda IdP.
- Identity record: `aws/transfer/<server-id>/research-user`, encrypted with `aws/secretsmanager`.
- Baseline record: synthetic password, low Transfer role, bucket-root home.
- Poisoned record: different synthetic password, high Transfer role, same home.
- Low and high roles trusted Transfer only from the exact account and server/user source ARN and
  could read disjoint `low/` and `high/` prefixes in the disposable bucket.
- Attacker allow: only `secretsmanager:PutSecretValue` on the exact secret ARN.
- Explicit denies: `iam:PassRole`, `s3:*`, `transfer:*`, `lambda:*`, and `apigateway:*`.
- The attacker had no `GetSecretValue` and did not know the baseline password from AWS.

## Results

| Case | Result |
| --- | --- |
| Baseline password reads `low/allowed.txt` | Connected; exact low marker recovered |
| Baseline password reads `high/protected.txt` | Connected; `Permission denied` |
| Restricted caller `GetSecretValue` | `AccessDeniedException` |
| Restricted caller `PutSecretValue` with explicit `Deny kms:*` | `AccessDeniedException: Access to KMS is not allowed` |
| Same exact-secret Put allow, no KMS allow and no explicit KMS deny | Succeeded; returned new version with `AWSCURRENT` |
| Attacker password reads `high/protected.txt` | Connected; exact high marker recovered |
| Old password after write | Authentication failed |

The successful call supplied a new client token and omitted `VersionStages`; Secrets Manager made the
new version current. `SecretString` held a complete JSON record, not a partial patch. The target role
already trusted Transfer. No `iam:PassRole` call occurred and no STS credentials were exposed; the
resulting escalation was the high role's S3 access as exercised by Transfer over SFTP.

## KMS boundary

The AWS-managed `aws/secretsmanager` key policy allows authorized Secrets Manager callers to use the
key through the service, so no positive KMS permission was required. Secrets Manager still requests
a new data key on the caller's behalf. Consequently, an explicit identity-policy `Deny kms:*`
blocked `PutSecretValue`. A customer-managed key may require `kms:GenerateDataKey` in the caller and
key policy, ideally constrained with `kms:ViaService` and the secret encryption context.

## Logging

- `PutSecretValue` is a default Secrets Manager management write. The event records the exact secret
  ARN and client request/version token but omits `SecretString`, hiding the selected password, role,
  policy, and home.
- The write triggers KMS `GenerateDataKey`; the KMS encryption context identifies the secret ARN and
  version.
- Each successful IdP lookup produced a default `GetSecretValue` management event under the Lambda
  role. The returned secret was omitted.
- API Gateway-to-Lambda `Invoke` and S3 object reads require optional data events. SFTP sessions need
  configured Transfer server logging.
- The successful `PutSecretValue` had not reached Event History during the fixture's first 20-second
  lookup; the earlier KMS-denied attempt had propagated later. Treat Event History as eventually
  consistent rather than assuming absence.

## Cleanup

Two fixture cycles ran. The first established that an explicit KMS deny blocks the AWS-managed-key
write; the second verified the attack. Both deleted their Transfer server rather than stopping it,
then removed the REST API, Lambda, secret (forced immediate deletion), bucket objects/bucket, inline
policies, and IAM roles. The first script version omitted the Lambda log group; it was found by the
independent inventory and deleted explicitly before the second cycle. The corrected cleanup removed
the second log group automatically. Final inventories were empty for matching servers, APIs,
functions, secrets (including planned deletion), roles, buckets, and log groups. API Gateway account
settings were never modified.
