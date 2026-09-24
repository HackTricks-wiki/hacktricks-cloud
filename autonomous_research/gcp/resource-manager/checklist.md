# Resource Manager — open ideas

Open ideas — Resource Manager / Org Policy.

- [ ] **Org Policy v2 CreatePolicy/UpdatePolicy audit-class confirmation.** Verify (live, on a
  disposable project-scoped policy) whether `orgpolicy.googleapis.com` v2 `CreatePolicy`/`UpdatePolicy`
  emit ADMIN_WRITE (always-on) or DATA_WRITE (off-by-default) log entries. Correct any wiki "Logs
  generated" rows that assert the wrong class. Verification-only (no wiki technique change unless the
  stealth story flips).
