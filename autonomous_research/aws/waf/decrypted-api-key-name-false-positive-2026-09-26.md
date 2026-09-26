# WAFv2 `GetDecryptedAPIKey` — name false positive, excluded 2026-09-26

## Result

Do not promote this operation as credential disclosure. Despite its name and API description saying it
returns a key “in decrypted form,” the authoritative response schema contains only:

- `CreationTimestamp`
- `TokenDomains`

The request itself requires the caller to provide the existing encrypted `APIKey`. There is no plaintext
key field in the response.

## Security interpretation

WAF CAPTCHA API keys are encrypted capability/configuration blobs designed to be copied into client-side
JavaScript. Their token-domain list authorizes which browser origins may use the CAPTCHA integration.
Possessing one is therefore not analogous to obtaining an AWS credential or a server-side secret, and
`GetDecryptedAPIKey` adds only metadata inspection for a value the caller already knows.

Potentially useful adjacent actions are ordinary configuration operations:

- `CreateAPIKey` creates a new immutable browser integration key for up to five domains.
- `ListAPIKeys` inventories existing encrypted keys and domain metadata.
- `DeleteAPIKey` revokes a key, although AWS warns that global disallowance can take up to 24 hours.

None is a distinct privesc, persistence, post-exploitation secret-disclosure, or unauthenticated-access
primitive by itself. A malicious domain must still be accepted by the protected web ACL's token-domain
configuration, and the browser key does not grant AWS API access.

## Test decision and cleanup

No AWS call or resource creation was needed: the request/response contract conclusively disproves the
secret-output hypothesis. Creating a disposable key would only reproduce public configuration behavior
and leave a potentially usable key during the documented deletion propagation window. No resource or
account setting was changed.

## Sources

- <https://docs.aws.amazon.com/waf/latest/APIReference/API_GetDecryptedAPIKey.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_CreateAPIKey.html>
- <https://docs.aws.amazon.com/waf/latest/APIReference/API_DeleteAPIKey.html>
- <https://docs.aws.amazon.com/waf/latest/developerguide/waf-js-captcha-api-key.html>
