# Route 53 Domains cross-account registration transfer — 2026-09-30

## Outcome

Documentation-validated expected functionality that clears the public-book bar:
`route53domains:TransferDomainToAnotherAwsAccount` plus destination-side
`route53domains:AcceptDomainTransferFromAnotherAwsAccount` can move a domain registration from a
victim account into an attacker-controlled AWS account. This is service-level privilege escalation
and asset theft, not IAM privilege escalation.

No AWS vulnerability was identified and no private report was created.

## Authorization model

The AWS Service Authorization Reference maps the source and destination APIs to exactly one IAM
action each:

- source: `route53domains:TransferDomainToAnotherAwsAccount`
- destination: `route53domains:AcceptDomainTransferFromAnotherAwsAccount`

Route 53 Domains defines no resource ARN types and no service-specific condition keys. Both actions
must therefore use `Resource: "*"`. The source API accepts only the domain name and 12-digit target
account ID, and returns an operation ID plus the password required by the destination. No
`ListDomains`, `GetDomainDetail`, EPP-code retrieval, transfer-lock mutation, or PassRole action is
part of the direct API request.

The attacker needs control of the destination account to authorize the accept call. The transfer
request expires after three days. AWS also documents that a registration cannot be moved between
AWS accounts during its first 14 days.

## Impact boundaries

- The **registration** moves to the destination account after acceptance.
- The Route 53 hosted zone does not move. Existing resolution is unaffected merely because the
  registration and hosted zone are in different accounts.
- The new registration owner can subsequently use permissions in its own account to alter contacts,
  nameservers, renewal, or transfer state. This makes takeover of DNS/email/certificate-validation
  paths possible, but those effects are follow-on changes rather than an automatic result of the
  internal transfer.
- The source can cancel only before destination acceptance; the destination can reject instead.

## Telemetry

AWS documents that every Route 53 API is recorded as a CloudTrail management event. Domain
registration event names begin with a lowercase letter and use
`route53domains.amazonaws.com`. The key events are:

- `transferDomainToAnotherAwsAccount` in the source account
- `acceptDomainTransferFromAnotherAwsAccount` in the destination account
- optional `cancelDomainTransferToAnotherAwsAccount` or
  `rejectDomainTransferFromAnotherAwsAccount`

The technique is Low stealth because it requires cross-account writes, produces a pending transfer,
and results in an observable ownership change. The returned password should be handled as sensitive
response data; public coverage does not claim that CloudTrail retains it.

## Live-account safety check

Assumed the authorized administrator role and called only `ListDomains` in `us-east-1`, projecting
the response to a count. Result: **0 registered domains**. No domain name or registration data was
returned to the research log.

Because an end-to-end test would require registering or transferring a real domain and would create
external ownership/billing state, no transfer API was invoked and no fixture was created. Cleanup was
therefore vacuous: the test created zero Route 53 Domains, hosted zones, IAM identities, or policies.

## Deferred defect hypotheses (require a disposable real-domain fixture)

- destination-account binding of the returned password
- password replay after cancel, reject, expiry, or successful acceptance
- cancel/accept and multiple-accept concurrency races
- Unicode/punycode normalization mismatches between initiation and acceptance
- leakage of the returned password into telemetry or unrelated status/read APIs

Do not test these against a production domain. A later run needs a deliberately purchased disposable
domain, a second explicitly authorized AWS account, and a recovery/cleanup plan that accounts for the
14-day transfer restriction.

## Primary sources

- https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_TransferDomainToAnotherAwsAccount.html
- https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_AcceptDomainTransferFromAnotherAwsAccount.html
- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-transfer-between-aws-accounts.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_route53domains.html
- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/logging-using-cloudtrail.html
