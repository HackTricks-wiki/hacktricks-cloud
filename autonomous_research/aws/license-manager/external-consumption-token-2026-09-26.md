# License Manager external consumption token — reasoned exclusion 2026-09-26

## Candidate

For a seller-issued license, `license-manager:CreateToken` returns a refresh JWT whose default
validity is 365 days. Its holder can call `GetAccessToken` to obtain one-hour OIDC tokens and then
use `sts:AssumeRoleWithWebIdentity` against a role that trusts the built-in federated principal
`openid-license-manager.amazonaws.com`.

This is a genuine bearer-credential and persistence primitive, but it is specific to License
Manager's customer-without-an-AWS-account flow. AWS's standard `AWSLicenseManagerConsumptionRole`
has only `CheckoutLicense`, `CheckInLicense`, `ExtendLicenseConsumption`, and `GetLicense` on `*`.
It is therefore not general AWS privilege escalation in the standard configuration. It becomes a
meaningful account-access technique only when an existing custom trusting role has broader policy or
weak `amr`/issuer conditions.

## Boundaries established

- `CreateToken` can be scoped to the exact seller-license ARN and supports resource-tag conditions.
- The creator supplies `RoleArns` and up to three token properties; no `iam:PassRole` dependency is
  documented. The current API contract explicitly says License Manager does not check whether the
  embedded roles are in use. This is not direct role delegation: STS still evaluates the target
  role's `AssumeRoleWithWebIdentity` trust policy when the access token is redeemed.
- The raw refresh token is returned only when created. `ListTokens` returns metadata, not the token.
- `DeleteToken` revokes it.
- `GetAccessToken` is authorized on `*` for IAM callers, but the intended external-customer flow is
  bearer-token redemption without AWS credentials.
- `AssumeRoleWithWebIdentity` requires no identity-policy permission from the token holder; the
  target role trust policy is the boundary. AWS's example trusts the federated principal
  `openid-license-manager.amazonaws.com` and constrains its `amr` to the expected token-issuer account.

A no-sign-request probe with a synthetic invalid JWT reached token validation and returned
`Invalid token`, consistent with the documented bearer-token flow. No genuine token was used or
created.

## Lab preflight and test decision

Account `228478051196` in `us-east-1` is not onboarded:

- `ListLicenses`, `ListReceivedLicenses`, `ListTokens`, and `GetServiceSettings` returned
  `Service role not found`.
- `AWSServiceRoleForAWSLicenseManagerRole` and `AWSLicenseManagerConsumptionRole` do not exist.
- No role trusts `openid-license-manager.amazonaws.com`.
- There is no seller-license resource, suitable `SIGN_VERIFY` KMS key, or recent `CreateLicense` /
  `CreateToken` Event History.

A disposable end-to-end fixture would require service onboarding, a seller-issued license, normally
an asymmetric customer-managed KMS signing key, and an OIDC-trusting role. Seller-license metadata is
cross-Region, and KMS deletion has a mandatory waiting period. That persistent residue is not
justified for a niche primitive whose security boundary is already clear, so no mutation was made
and there is nothing to clean up.

## Revisit condition

Retest in an existing seller-license deployment. Prioritize custom roles that trust the License
Manager OIDC principal and grant permissions beyond license consumption. Verify issuer/`amr` and
audience enforcement, token revocation, exact CloudTrail fields for creation/deletion/redemption, and
whether caller-selected role ARNs can target any weakly conditioned compatible role.

## Sources

- <https://docs.aws.amazon.com/license-manager/latest/APIReference/API_CreateToken.html>
- <https://docs.aws.amazon.com/license-manager/latest/APIReference/API_GetAccessToken.html>
- <https://docs.aws.amazon.com/license-manager/latest/userguide/granting-temporary-credentials.html>
- <https://docs.aws.amazon.com/license-manager/latest/userguide/seller-issued-license-requirements.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_license-manager.html>
- <https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSLicenseManagerConsumptionPolicy.html>
