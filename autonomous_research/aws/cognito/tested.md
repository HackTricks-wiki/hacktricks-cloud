# Cognito — tested

Cognito already has: unauthenticated-enum page, privesc page, persistence page (see book).

## Negatives / deferrals (don't re-test blindly)

- **Passkey/WebAuthn authenticator-enrollment persistence** — DEFERRED, not disproven. Blocked on
  needing a WebAuthn attestation lib to produce a valid attestation object. Moved to checklist.
- **TOTP authenticator persistence** — judged weak/low-value (needs to reset the user's TOTP secret,
  which is noisy and equivalent to a password reset). Not documented.
