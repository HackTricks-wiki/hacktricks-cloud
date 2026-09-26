# App Configuration — Candidate Attacks (not yet lab-fired)

- [ ] Build the four-key revocation matrix: rotate one read-write/read-only key at a time and confirm
      whether old credentials fail immediately on every endpoint; repeat after `disableLocalAuth=true`.
- [ ] On a disposable store with a replica, test whether key rotation and `disableLocalAuth` propagate
      atomically across the primary and replica endpoints. Continued use beyond documented propagation
      would be a private-report candidate, not a wiki technique.
- [ ] Test whether an archived snapshot remains readable until its retention expiry and whether deleting
      every matching live key changes that behavior; document the exact eviction controls.
