# Automation — Candidate Attacks (not yet lab-fired)

- [ ] Build a **working** watcher execution loop (correct action/watcher-runbook contract) to confirm
      whether the *executed* runbook body runs off Activity Log (data-plane) even though `watchers/write`
      is logged — i.e., is the execution itself the stealth part?
- [ ] Confirm min token/MI reachable from a webhook-triggered runbook: does the job run under the
      Automation account's **system-assigned MI** by default, and what sub-scope does it inherit?
