# STS credential-vending checklist

## Completed

- [x] Enable outbound identity federation briefly, issue only 60-second synthetic-canary JWTs, disable
  it, wait for expiration, and independently verify role/policy/setting cleanup.
- [x] Prove `sts:GetWebIdentityToken` resource scoping to
  `arn:aws:sts::<account-id>:self` with fixed audience, maximum duration, and signing-algorithm
  conditions under an isolated principal.
- [x] Negative-test a different audience, a duration above the policy cap, and a tag without the
  dependent `sts:TagGetWebIdentityToken` authorization.
- [x] Verify regional-endpoint behavior, OIDC discovery/JWKS matching, and JWT claims without retaining
  the JWT; confirm from AWS documentation that `AssumeRoleWithWebIdentity` rejects outbound tokens.
- [x] Confirm that an assumed-role caller's `sub` is the underlying IAM role ARN rather than the
  assumed-role session ARN.
- [x] Confirm default CloudTrail management-event fields and that the response logs a token ID and
  expiration, not the JWT; `TagGetWebIdentityToken` is not a separate API event.
- [x] Confirm disable blocks new issuance but public discovery/JWKS remain available for validation.
- [x] Exclude `GetDelegatedAccessToken` as partner-workflow-only after account inventory and a bounded
  invalid-token preflight.

## Future high-signal variations

- [ ] With an explicitly authorized controlled relying party, test end-to-end external authorization
  and revocation behavior without transmitting a bearer token to any third party.
- [ ] Test multiple audiences and `ES384` under equivalently constrained policies; publish only if the
  boundary differs from AWS documentation.
- [ ] Test session/source-context claim changes across multiple assumed-role sessions and document the
  exact relying-party binding strategy where session-level separation is required.
