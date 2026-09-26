# Cognito Identity Pool CloudTrail audit — 2026-09-26

## Finding

Current [AWS Cognito CloudTrail documentation](https://docs.aws.amazon.com/cognito/latest/developerguide/logging-using-cloudtrail.html) classifies `GetCredentialsForIdentity`, `GetId`, `GetOpenIdToken`, `GetOpenIdTokenForDeveloperIdentity`, and `UnlinkIdentity` as **opt-in data events** on `AWS::Cognito::IdentityPool`. The prior book tables classified the first, second, and fourth as management events that could never generate records. Their earlier live tests checked default CloudTrail/Event History only; that is consistent with the current documentation, which says data events are disabled by default.

The AWS guide supplies an advanced selector example with `eventCategory = Data` and `resources.type = AWS::Cognito::IdentityPool`. No data-event-enabled trail was tested in this audit, so the book cites documented support rather than claiming a new live verification. No AWS resources were created.

## Book corrections

- Corrected the event type and default logging state across Cognito privilege escalation and persistence techniques.
- Replaced absolute statements about invisible token and credential exchange with configuration-specific language.
- Added CloudTrail configuration guidance to Identity Pool enumeration.

## Candidates to revisit

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| Abuse of developer-authenticated identities to obtain the authenticated pool role | Expected | Previously verified live; book covers | Recheck minimum IAM and CloudTrail data event contents with an isolated pool/trail when practical |
| Cross-account identity-pool credential request absent from an enabled owner trail | Potential unexpected | No evidence; account attribution needs testing | Use two isolated accounts, inspect owner and caller trails, then delete resources |
| Missing CloudTrail record with correct identity-pool selector | Potential unexpected | No evidence | Reproduce with selector and exact API; report only if confirmed |
