# IVS Chat — open ideas

- [x] `CreateChatToken` exact-room minimum permission and arbitrary user/capability impact — verified.
- [x] Token sequential replay, live duplicate, mutation, Region binding, and five eight-way races —
  failed closed; no AWS report.
- [ ] Cross-account room resource-policy behavior — revisit only with a second explicitly authorized
  account; do not infer it from same-account resource scoping.
- [ ] Token revocation on room deletion/update — low priority unless AWS documents an immediate
  revocation guarantee; propagation alone would not clear the reporting bar.
