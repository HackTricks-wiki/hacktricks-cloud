# Storage — Candidate Attacks (not yet lab-fired)

- [ ] Live-fire wildcard-CORS exfil: set `*` CORS on blob, confirm cross-origin browser read of private
      blobs via a user-delegation/SAS context, record whether the CORS write is the only logged event.
- [ ] Confirm disabling versioning+soft-delete+change-feed removes recoverability with a single
      `storageAccounts/write` and what one Activity Log entry it produces.
- [ ] Storage Tasks: fire a benign no-op task assignment on a throwaway account to confirm the MI-backed
      recurrence model + logs (then delete).
