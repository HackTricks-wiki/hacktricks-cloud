# Automation — Candidate Attacks (not yet lab-fired)

- [ ] Build a **working** watcher execution loop (correct action/watcher-runbook contract) to confirm
      whether the *executed* runbook body runs off Activity Log (data-plane) even though `watchers/write`
      is logged — i.e., is the execution itself the stealth part?
- [ ] Confirm min token/MI reachable from a webhook-triggered runbook: does the job run under the
      Automation account's **system-assigned MI** by default, and what sub-scope does it inherit?
- [ ] Resolve the custom Runtime Environment package authorization boundary before documenting it:
      live denial names `Microsoft.Automation/automationAccounts/runtimeEnvironments/packages/write`,
      but that action is absent from the provider-operation catalog and Azure rejects it in a custom
      role. Identify an assignable least-privilege action or broader working wildcard/role and verify
      package replacement plus execution. Until then, keep this out of the public book.
