# Cloud Shell research checklist

## Completed 2026-09-28

- [x] Separate interactive-user authorization from VM metadata service-account credentials.
- [x] Bound access-token recovery to a pre-authorized, already-compromised session.
- [x] Reconcile ephemeral VM/container, private persistent home directory and root-user behavior.
- [x] Remove the historical Docker host-socket escape and generic open-proxy instructions.
- [x] Record local versus downstream API telemetry without inventing a Cloud Shell audit contract.
- [x] Confirm no cloud or local test state was created during the documentation pass.

## Safe future validation

- [ ] In an explicitly disposable user session, capture token lifetime/scopes and whether local
      `gcloud auth print-access-token` creates any Cloud Shell platform signal. Never print the token
      into retained logs; inspect only non-secret claims and restart the VM immediately afterward.
- [ ] Compare authorized versus never-authorized sessions and VM restart revocation. Do not automate
      or bypass the user consent prompt, and delete any temporary SSH/public-key access.
- [ ] Inspect metadata identities only by email/scopes. Do not retain a bearer token, and do not
      publish a technique unless a distinct identity has useful permissions beyond the user-session
      token boundary.
