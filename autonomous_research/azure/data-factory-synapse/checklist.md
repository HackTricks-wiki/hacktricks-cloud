# Data Factory / Synapse — Candidate Attacks (not yet lab-fired)

Cost note: an ADF instance itself is cheap; **debug/Spark compute** may cost — check <$5/30min gate first.

- [ ] Live-fire ADF pipeline **debug** RCE as the factory MSI (custom activity / Azure Function / Web
      activity) with min perms; confirm token reachable and NOT in Activity Log (data-plane).
- [ ] Verify `getGitHubAccessToken` returns a usable token (currently UNVERIFIED).
- [ ] Confirm Synapse `bigDataPools` Spark notebook RCE as workspace MSI (UNVERIFIED) — mind Spark cost.
- [ ] Stay INSIDE client infra — any cross-tenant IR escape is a 0day, report privately, do not wiki.
