# Cognito `AdminDeleteSoftwareToken` authentication downgrade — 2026-09-30

## Result

Verified expected functionality and shipped it as a bounded Cognito privilege-escalation technique. A principal with only `cognito-idp:AdminDeleteSoftwareToken` on one exact user-pool ARN can delete a known user's registered TOTP factor. The action does not return the TOTP secret and does not disclose or reset the password.

Security impact depends on the user's other factors and the pool-wide MFA policy:

- With `MfaConfiguration=OPTIONAL`, TOTP as the only configured MFA factor, and a valid password, the next compatible password authentication returns tokens without an MFA challenge.
- With `MfaConfiguration=ON` and no other factor, authentication returns `MFA_SETUP` and no tokens. This is not a dead end for an attacker who knows the password: the returned challenge session authorizes public `AssociateSoftwareToken` and `VerifySoftwareToken` calls, allowing registration of an attacker-controlled TOTP factor and completion of sign-in.
- If another factor is available, AWS documents that sign-in falls back to that factor. The delete action does not disable SMS, email OTP, passkeys, or the pool-wide MFA requirement.
- Without a password or separate password-reset primitive, this is factor deletion / denial of service, not standalone account takeover.

Optional `cognito-idp:AdminGetUserAuthFactors` reconnaissance returns the user's preferred MFA setting, enabled MFA methods, and configured authentication factors, but no factor secret. It can identify users whose TOTP deletion will leave no fallback factor.

## Exact-permission live test

A disposable Essentials-tier user pool, public app client, and one local user were created in `us-east-1`. TOTP was enrolled with an access token and a locally generated RFC 6238 code.

Before deletion, `AdminGetUserAuthFactors` returned:

```json
{
  "Preferred": "SOFTWARE_TOKEN_MFA",
  "MFA": ["SOFTWARE_TOKEN_MFA"],
  "Factors": ["PASSWORD", "SOFTWARE_TOKEN"]
}
```

An STS session was restricted to exactly:

```json
{
  "Effect": "Allow",
  "Action": "cognito-idp:AdminDeleteSoftwareToken",
  "Resource": "arn:aws:cognito-idp:us-east-1:228478051196:userpool/<test-pool-id>"
}
```

The same operation against a different synthetic pool ARN returned `AccessDeniedException`. Against the exact test pool it succeeded without list, get, MFA-preference, password-reset, pool-update, or authentication permissions.

Observed state transitions:

| Pool policy / state | Before deletion | After exact-permission deletion |
| --- | --- | --- |
| `OPTIONAL`, TOTP only | `SOFTWARE_TOKEN_MFA` challenge | no challenge; `AuthenticationResult.AccessToken` present |
| `ON`, TOTP only | TOTP enrolled | `MFA_SETUP`; no access token |

The required-MFA setup flow was also exercised before the second deletion: `AdminInitiateAuth` returned `MFA_SETUP`, its session was accepted by `AssociateSoftwareToken`, `VerifySoftwareToken` returned a continuation session, and `AdminRespondToAuthChallenge` completed enrollment. This confirms why a password holder can replace the deleted factor rather than merely lock the victim out.

A separate final confirmation used a public app client with `ALLOW_USER_PASSWORD_AUTH` and `--no-sign-request` for every user-side call. Before deletion, unsigned `InitiateAuth` returned `SOFTWARE_TOKEN_MFA`. After the exact-action delete, the same unsigned call returned tokens in `OPTIONAL`; after switching the pool to `ON`, it returned `MFA_SETUP` and no tokens. Unsigned `AssociateSoftwareToken`, `VerifySoftwareToken`, and `RespondToAuthChallenge` then registered a new locally controlled TOTP secret and returned tokens. This proves the post-deletion takeover flow requires no additional IAM permission when a compatible public client and valid password are available.

## Telemetry

The current AWS CloudTrail contract says Cognito user-pool API calls are management events and obscures private user/authentication fields with `HIDDEN_DUE_TO_SECURITY_REASONS`. Detection should alert on `AdminDeleteSoftwareToken` from any principal outside an approved recovery workflow and correlate it with `InitiateAuth`, `MFA_SETUP`, `AssociateSoftwareToken`, `VerifySoftwareToken`, and `RespondToAuthChallenge`.

Event History initially had not indexed even `CreateUserPool` after approximately one minute, but all relevant records appeared on a later poll. The two successful deletes were default management writes under `cognito-idp.amazonaws.com`; each retained `userPoolId`, masked `username` as `HIDDEN_DUE_TO_SECURITY_REASONS`, set `readOnly: false`, and had `responseElements: null`. `AdminGetUserAuthFactors` was a default management read with the same visible pool ID, masked username, and null response. The read therefore does not spill returned factor metadata into CloudTrail.

Overall stealth: **Low**. The prerequisite write is rare and management-logged, even though Cognito's redaction can hide the target username.

## Failed runs and cleanup evidence

The first exact-resource attempt constructed its resource ARN with the source profile's account ID instead of the assumed role's target account. AWS denied both the control and intended call, so it produced no behavioral evidence. Exported restricted credentials also overrode the admin profile inside the initial cleanup trap; a fresh-process inventory caught the still-existing pool, and that exact pool was then deleted manually.

A second attempt reached the intended no-content API but the local environment's invalid default CLI output value (`asd`) caused a formatter error, making the call result ambiguous. Its cleanup call nevertheless removed the pool, confirmed by exact `ResourceNotFoundException` and empty inventory. The final test forced JSON output everywhere and changed the trap to unset session credentials before deletion.

Final `ListUserPools` inventory in `us-east-1` is empty. All four disposable pools are absent. Deleting each pool also removed its app client and user; no IAM role/policy, Lambda trigger, domain, identity pool, SMS configuration, passkey, or external resource was created. The restricted STS sessions expired naturally.

## Classification

Expected AWS functionality, not an AWS vulnerability. No private bug-bounty report was created.

## Sources

- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminDeleteSoftwareToken.html
- https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminGetUserAuthFactors.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-mfa-totp.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/authentication-flows-public-server-side.html
- https://docs.aws.amazon.com/cognito/latest/developerguide/logging-using-cloudtrail.html
