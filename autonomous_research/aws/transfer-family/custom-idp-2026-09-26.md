# Transfer Family custom identity-provider research — 2026-09-26

## Outcome

Verified three useful expected attack paths on disposable public SFTP servers:

1. `transfer:UpdateServer` on the exact server can replace the direct-Lambda IdP with an already
   server-authorized Lambda, without `iam:PassRole`.
2. `lambda:UpdateFunctionCode` on the already-wired IdP Lambda can accept an attacker login, capture
   passwords, and choose a Transfer-trusting S3/EFS role, without any Transfer, Invoke, PassRole, or
   direct storage permission.
3. `apigateway:PATCH` on the exact status-200 integration response plus `apigateway:POST` on that
   REST API's deployment collection can replace the IdP response with an attacker-selected role/home
   and activate it on the production stage, with an explicit `iam:PassRole` deny.

All three reached real S3 marker objects through SFTP. These are expected authorization consequences and
were added to the public privesc page. The exact synthetic password was also recovered from the
Lambda log after the handler intentionally printed its event, producing a separate post-exploitation
technique for unsafe custom-IdP logging.

## Live fixture and minimum permissions

- Region/account: `us-east-1`, authorized account `228478051196`.
- One public SFTP server at a time; S3-backed; direct Lambda or API Gateway custom IdP.
- Two marker prefixes and two roles restricted to the disposable bucket.
- Transfer-role trusts restricted by account and `user/<server-id>/*` source ARN.
- Lambda invoke policies restricted to the exact `server/<server-id>` ARN after bootstrap.
- Restricted updater: only `transfer:UpdateServer` on the exact server. `DescribeServer` was denied.
- Restricted coder: only `lambda:UpdateFunctionCode` on the exact IdP function.
- Neither restricted caller had PassRole, Lambda Invoke, logs-read, or S3 permissions.
- API Gateway fixture used the exact documented
  `/servers/{serverId}/users/{username}/config` GET resource and an `AWS_IAM` method.
- Restricted patcher: only `apigateway:PATCH` on the exact `GET`/`200` integration-response ARN and
  `apigateway:POST` on that API's deployment collection, limited to `StageName=prod`; explicit PassRole deny.
- Restricted oracle: only `transfer:TestIdentityProvider` on one exact user ARN; DescribeServer denied.

## End-to-end expected-attack results

| Case | Result |
| --- | --- |
| UpdateServer-only caller changes `IdentityProviderDetails.Function` | HTTP 200; no PassRole gate |
| Real login through replacement IdP | Connected; read both high-role marker prefixes |
| UpdateFunctionCode-only caller replaces wired IdP | Succeeded; no Transfer/PassRole permission |
| Real login through poisoned wired IdP | Connected; read both high-role marker prefixes |
| Lambda event | Contained exact plaintext synthetic password |
| `FilterLogEvents` on Lambda group | Recovered exact canary; event itself was a default management read |
| Integration-response PATCH with no GET | Succeeded; replaced only `application/json` template |
| Restricted production deployment | Succeeded without PassRole |
| Real login through static malicious API response | Connected; read protected marker through selected role |
| Exact-user `TestIdentityProvider` | Returned role/home/URL with DescribeServer denied |
| Oracle-supplied documentation `SourceIp` | Forwarded to IdP and satisfied its allow rule; real login from actual IP failed |

The escalation boundary is file-protocol access. Transfer does not return STS credentials, so a role
with unrelated administrator permissions does not automatically expose those permissions through
SFTP; the valuable target is a Transfer-trusting role with broad S3/EFS access.

## Two-factor / parser matrix

The server was switched to `PUBLIC_KEY_AND_PASSWORD`. A valid baseline used complete RSA-key and
password responses and a low role plus restrictive session policy.

| Case | Key response -> password response | Observed result |
| --- | --- | --- |
| Baseline | Low/restrictive -> Low/restrictive | Connected; allowed marker readable; denied marker blocked |
| Wrong password | Valid key, wrong password | Authentication failed |
| Wrong key | Wrong key, valid password | Authentication failed before password completed |
| Role control | High/restrictive -> High/restrictive | Connected; denied marker blocked |
| Policy omitted | High/omitted -> High/omitted | Connected; both markers readable |
| Base-role boundary | Low/omitted -> Low/omitted | Connected; denied marker blocked |
| Mismatched role | Low/restrictive -> High/omitted | Connected as high/base; both markers readable |
| Reverse role | High/omitted -> Low/restrictive | Connected as low/restricted |
| Mismatched policy | High/restrictive -> High/permissive | Connected; permissive password policy effective |
| Reverse policy | High/permissive -> High/restrictive | Connected; restrictive password policy effective |
| Mismatched home | High/restrictive `/allowed` -> `/denied` | Connected with password-response home |
| Password returns `PublicKeys` | Same complete response plus keys | Authentication failed |
| `{not-json` / truncated Policy | Same malformed value in both | Authentication failed |
| Duplicate top-level `Statement` | Same ambiguous Policy in both | Connected, but every operation failed `Unable to AssumeRole for user` |
| Low role + permissive Policy | Same in both | Connected; base low role still blocked denied marker |
| Empty Policy | High/empty -> High/empty | Connected; both markers readable |
| Omitted Policy | High/omitted -> High/omitted | Connected; both markers readable |

The password response supplies the effective authorization fields when factor responses differ.
This is worth retaining as a regression case, but it is not independently exploitable: the custom
IdP owns both authentication decisions and may return the high role directly. No cross-principal,
cross-account, or service-authorization boundary was crossed. Malformed nonempty policies did not
yield access. Therefore no local AWS vulnerability report was created.

## CloudTrail and telemetry

- `UpdateServer` was a default management event and included the replacement function ARN.
- Lambda code replacement was the default management event `UpdateFunctionCode20150331v2`; rules
  matching the unsuffixed SDK name will miss it.
- `FilterLogEvents` was a default management read and recorded the log group/filter, not returned log
  contents.
- Transfer-to-Lambda Invoke is an optional Lambda data event.
- SFTP authentication is not a Transfer API management event; it requires configured server logging.
- S3 object operations require optional S3 data events.
- There was no standalone PassRole event because none of the verified attack paths performed PassRole.
- `UpdateIntegrationResponse` was a default management write and recorded the entire replacement
  response template, including the selected role and home.
- `CreateDeployment` was a default management write and recorded the REST API, stage, description,
  and deployment ID.
- `TestIdentityProvider` was a default management event with `readOnly:false`. It redacted
  `userPassword`, but recorded the caller-chosen `sourceIp` and its full response, including role,
  home, identity-provider type, request ID, and API URL.

## API Gateway response-template matrix

The first cycle used a generic proxy resource. The integration update and deployment both succeeded,
but Transfer received no role; this was a fixture mismatch and was not treated as a service result.
The second cycle used the documented route hierarchy and verified the full boundary:

| Case | Result |
| --- | --- |
| Baseline direct request from non-allowlisted IP | `{}` |
| Exact-user TestIdentityProvider with chosen allowlisted source IP | Role/home returned |
| Real baseline SFTP from actual source IP | Authentication failed |
| Restricted integration-response GET | AccessDenied |
| Restricted response-template PATCH | Succeeded |
| Restricted stage deployment | Succeeded |
| Immediate TestIdentityProvider | Initially failed during propagation |
| Propagated TestIdentityProvider | Static role/home returned |
| Real password SFTP | Connected and read marker |
| Patcher PassRole | Explicitly denied and unnecessary |

The behavior is expected: an API Gateway response mapping sits inside the trusted custom IdP and may
transform a backend denial into a complete authorization response. No AWS security boundary was
crossed, so no local vulnerability report was created.

## Cleanup

Seven short test cycles were needed to remove client-fixture ambiguity (SDK absence, SSH two-factor
handling, username minimum, and Paramiko's representation of AWS's partial-auth signal). Every cycle
deleted its server immediately in `finally`; no server was merely stopped. Final independent
inventory returned zero matching Transfer servers, Lambda functions, IAM roles, S3 buckets, and log
groups. Total endpoint cost remained far below the authorized ceiling.
