# Privileged Access Manager — open ideas

Open ideas — Privileged Access Manager.

No open candidate (hypothesis tested + reframed correctly). PAM API was left enabled after teardown
(free, no resources).

## 2026-09-28 follow-ups

- [ ] If an already-existing disposable entitlement is available, capture the v1 `CreateGrant` ->
      `PAMActivateGrant` -> scope-specific `SetIamPolicy` correlation and final removal. Do not create
      an entitlement solely for telemetry testing.
- [ ] Re-check multi-level/multi-party approval behavior after Preview reaches GA. Preserve the
      current hard boundary that a requester cannot approve their own request.
- [ ] Test notification timing only with consenting recipients. Email notification is a defensive
      signal, not a separate attack primitive.
