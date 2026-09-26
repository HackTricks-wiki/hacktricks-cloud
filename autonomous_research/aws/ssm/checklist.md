# Systems Manager — attack checklist

## JIT node access

- [x] Documentation/API-model review: `StartAccessRequest` + approved request + `GetAccessToken` vends constrained AWS credentials that can call `StartSession` without the requester holding standing `StartSession` permission.
- [x] Account preflight: JIT service-linked role absent; no auto/manual approval documents; no managed nodes; no unified-console Quick Setup configuration manager. Do not enable account/organization-wide JIT in this shared account merely to force a test.
- [ ] In an account where JIT is already enabled, confirm the minimal two-action policy with an exact test node and an auto-approval policy restricted to the requester.
- [ ] Confirm original credentials are denied direct `StartSession`, while the three returned credential fields start a harmless session.
- [ ] Capture exact CloudTrail response redaction for `GetAccessToken` and confirm no secret credential material appears.
- [ ] Confirm a session remains open past approval-window expiry unless Session Manager duration/idle preferences terminate it.

See `jit-node-access-2026-09-26.md`.

