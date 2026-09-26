# STS GetDelegatedAccessToken — reasoned exclusion 2026-09-26

## Decision

Do not document `sts:GetDelegatedAccessToken` as a standalone general privilege-escalation technique.
The API does return an access key, secret key, and session token, but it is the final exchange step in
**AWS Partner temporary delegation**, not a credential-minting path unlocked by the IAM action alone.

## Required workflow

AWS documents these prerequisites:

1. The provider is an eligible AWS Partner, with participating provider accounts registered through
   the AWS onboarding process and pre-registered session-policy templates.
2. The provider creates a delegation request with IAM `CreateDelegationRequest`.
3. A customer-side principal reviews, associates, and accepts that request.
4. IAM delivers a trade-in/exchange token through the provider's registered SNS topic.
5. The provider presents that token to `GetDelegatedAccessToken` from the registered provider account.

The issued credentials are limited by the intersection of the approved customer principal and the
registered session policy. A trade-in token is provider-bound and may be exchanged repeatedly until
the approval expires, with a documented maximum delegation duration of 12 hours (four hours for a
root approver).

The Service Authorization Reference lists `sts:GetDelegatedAccessToken` as a Write action without
resource-level scoping. That does not bypass possession and workflow validation of the trade-in token.

## Read-only/preflight evidence

In the authorized lab account:

- `iam list-delegation-requests` returned zero requests.
- SNS topic inventory found no delivery topic for this workflow.
- CloudTrail Event History contained no `CreateDelegationRequest`, `AcceptDelegationRequest`,
  `SendDelegationToken`, or `GetDelegatedAccessToken` events from a real workflow.
- A bounded call using an obviously synthetic trade-in token returned
  `ValidationError: Invalid trade-in token`.

No resource, IAM policy, SNS topic, credential, or persistent setting was created. A representative
fixture is not independently disposable: it requires AWS Partner onboarding, a registered provider
account and policy template, plus deliberate approval by a separate customer-side principal.

## Security interpretation

Possession of a **valid** trade-in token can be security-relevant because it can repeatedly yield
temporary credentials during the approved window. The meaningful review surface is therefore the
partner onboarding, delegation request and approval, token-delivery topic, registered policy template,
and credential use—not an assumed standalone `sts:GetDelegatedAccessToken` privilege-escalation path.

The customer-side risk of accepting and finalizing an attacker-controlled delegation request is a
distinct IAM workflow and is already documented on the public IAM privilege-escalation page. Revisit
the STS exchange boundary only if the account already participates in AWS Partner temporary delegation
and a controlled, customer-approved request is available for testing.

## Sources

- <https://docs.aws.amazon.com/STS/latest/APIReference/API_GetDelegatedAccessToken.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies-temporary-delegation-partner-guide.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/temporary-delegation-building-integration.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies-temporary-delegation.html>
- <https://docs.aws.amazon.com/IAM/latest/UserGuide/temporary-delegation-cloudtrail.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_sts.html>
