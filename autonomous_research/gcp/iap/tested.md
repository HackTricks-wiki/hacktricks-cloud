# Iap — tested

Identity-Aware Proxy (IAP). Covered: unauth `allUsers`→`iap.httpsResourceAccessor` bypass; persistence
page (durable resource-IAM binding + OAuth client-secret backdoor via `clientauthconfig.clients.*`).

## Correction applied
- IAP has NO documented Cloud Audit method for the runtime `AuthorizeUser` access decision — "Data
  Access" claims replaced with "None — no documented IAP Cloud Audit method."

## Standing items
- Beta egress `iap.webServiceVersions.egressViaIAP` audit class unconfirmed.
- `serviceusage.contentsecuritypolicy.*` / `groups.*` / `effectivemcppolicy.get` have no verified
  offensive framing yet.
