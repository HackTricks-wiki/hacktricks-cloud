# Entity Resolution technique metadata audit — 2026-09-26

## Scope and result

Reviewed the existing `PutPolicy` self-grant and stored-workflow execution techniques against the
public API/service-authorization contracts. Both techniques were useful but lacked the repository's
required minimum-permission, impact, stealth, and technique-local logging metadata.

- `PutPolicy` is authorized on `*`; a known target ARN is supplied in the request. The first policy
  write can omit a revision token, while replacement requires the current token. `GetPolicy` is an
  optional way to recover it.
- A resource policy can grant supported Entity Resolution resource actions but cannot grant
  `iam:PassRole` or direct access to a configured output destination.
- `StartMatchingJob` only needs the exact workflow permission once its name/ARN is known. The stored
  workflow role performs the downstream input and output operations.

The public page now records the exact boundaries, scoped impact, persistence lifetime, stealth, and
default management events. No AWS call or resource creation was needed for this documentation audit.

## Sources

- <https://docs.aws.amazon.com/entityresolution/latest/apireference/API_PutPolicy.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_entityresolution.html>
- <https://docs.aws.amazon.com/entityresolution/latest/apireference/API_StartMatchingJob.html>
