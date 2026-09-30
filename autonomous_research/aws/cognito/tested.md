# Cognito — tested

Cognito already has: unauthenticated-enum page, privesc page, persistence page (see book).

## Negatives / deferrals (don't re-test blindly)

- **Passkey/WebAuthn authenticator-enrollment persistence** — DEFERRED, not disproven. Blocked on needing a WebAuthn attestation lib to produce a valid attestation object. Moved to checklist.
- **TOTP authenticator persistence** — judged weak/low-value (needs to reset the user's TOTP secret, which is noisy and equivalent to a password reset). Not documented.
- **`AdminDeleteSoftwareToken` TOTP removal** — VERIFIED separately as a useful exact-pool authentication downgrade. In an optional-MFA pool it restored password-only tokens; in a mandatory-MFA pool it returned `MFA_SETUP`, which a password holder can use to enroll an attacker-controlled token. Shipped in the Cognito privesc page; see `admin-delete-software-token-2026-09-30.md`.
