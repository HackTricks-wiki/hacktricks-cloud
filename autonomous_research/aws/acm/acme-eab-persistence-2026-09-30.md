# ACM ACME EAB credential and account-persistence audit — 2026-09-30

## Result

The September 2026 ACM model exposes a real external certificate-account persistence path:

- exact-EAB `GetAcmeExternalAccountBindingCredentials` returns both the key identifier and MAC secret;
- those credentials authorize one-time registration of an ACME account whose private account key is held by the client;
- certificate issuance/revocation is subsequently authorized through the IAM role stored on the EAB;
- AWS explicitly states that revoking the EAB does not affect already registered ACME accounts, which must be revoked independently.

Added ACME endpoint/binding/domain/account enumeration and one bounded ACM service-level persistence technique. This is expected AWS functionality, not a vulnerability candidate.

## Current-model delta

AWS CLI 2.34.45 lacked the complete ACME control plane. AWS CLI 2.37.6 adds 23 ACM operations covering endpoint, domain validation, EAB, account, tagging and certificate-domain-validation lifecycle, including the secret-returning getter.

The public feature launched in 2026 and received additional IAM/condition-key documentation on September 28, 2026. The client continues to use the ordinary `acm` service name; ACME protocol events use `acm-acme.amazonaws.com`.

## Safe live validation

Both permitted Regions initially returned empty `ListAcmeEndpoints` inventories. Unsigned listing failed with `MissingAuthenticationTokenException`.

A restricted STS session allowing only `acm:GetAcmeExternalAccountBindingCredentials` on one syntactically valid EAB ARN reached `ResourceNotFoundException`. The same request for a different EAB ARN was denied by the session policy. This proves exact-EAB resource binding without an existing secret fixture.

## Disposable fixture and blocked end-to-end branch

A public-CA ACME endpoint was created in `us-east-1` with one allowed RSA algorithm, no domain validation, no certificate tags and `Contact=NOT_REQUIRED`; it reached `ACTIVE` on the first poll. A disposable IAM role trusted `acm-acme.amazonaws.com` for `AssumeRole`, `TagSession`, and `SetSourceIdentity` and allowed only ACME-origin `acm:RequestCertificate`.

Creating a one-day EAB stopped at caller-side authorization:

```text
AccessDeniedException: ... is not authorized to perform: iam:PassRole on resource: ...:role/ht-acme-eab-20260930-a
```

This confirms the documented exact-role PassRole dependency and the lab's privilege limit. No EAB credential was created or retrieved, no ACME account was registered, and no domain/certificate/order existed. The current public contract is sufficient to publish the expected credential-to-account persistence path, but the book does not label it end-to-end live tested.

## Capability and impact boundary

- The EAB MAC key is a secret and can be retrieved repeatedly while the binding remains valid.
- Registration creates an external ACME account and client-held private key. EAB expiry/revocation stops new registration only; it is not account revocation.
- The account can request only domain names covered by current `VALID` endpoint validations and only algorithms allowed by the endpoint.
- ACM assumes the EAB's role for standard `acm:RequestCertificate` / `RevokeCertificate` authorization. The role's policy conditions, permission boundary and SCP remain effective. The client never receives role credentials or general AWS API access.
- The attacker holds each issued certificate private key. ACME-issued certificates are for customer-managed infrastructure and cannot attach to ACM-integrated ELB, CloudFront or API Gateway resources.

This is ACM service-level persistence and potential public-certificate impersonation, not account-wide IAM persistence.

## Telemetry

Live CloudTrail indexed:

- `ListAcmeEndpoints` as a default `acm.amazonaws.com` management read;
- exact and denied `GetAcmeExternalAccountBindingCredentials` reads with the requested EAB in `resources`; the post-IAM not-found request retained the ARN while the authorization denial omitted request parameters;
- successful `CreateAcmeEndpoint` as a management write with complete endpoint configuration and `AWS::CertificateManager::AcmeEndpoint` resource;
- denied `CreateAcmeExternalAccountBinding` as a management write against the exact endpoint, with parameters hidden by the pre-service PassRole failure.
- successful `DeleteAcmeEndpoint` as a management write retaining the exact endpoint in both request parameters and `resources`.

AWS's current logging contract additionally shows successful credential reads with `responseElements: null`, `NewAccount` as a default management event under `acm-acme.amazonaws.com`, and order/finalize/download as opt-in data events. PassRole does not generate a standalone CloudTrail event.

## Cleanup

The failure trap requested endpoint deletion and removed the role/inline policy. The endpoint transitioned through `DELETING` and returned `ResourceNotFoundException` on the third five-second poll. Final regional endpoint inventory is empty and the exact role returns `NoSuchEntity`. The isolated 47 MB Certbot environment was deleted. No EAB, ACME account, domain validation, certificate, order, hosted zone, DNS record, private CA or service-linked role was created.

## Follow-ups

- In a purpose-built account whose administrator can pass a disposable ACME role, register one account, revoke the EAB, prove the account remains usable, then explicitly revoke the account and delete the endpoint.
- Test whether one EAB can register multiple accounts and whether `LastUsedAt` makes each reuse immediately visible.
- Exercise exact domain/scope, `acm:DomainNames`, `acm:Export`, key-algorithm and certificate-tag enforcement with a controlled public domain before considering any authorization-defect hypothesis.
