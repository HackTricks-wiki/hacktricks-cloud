# Azure Container Registry — Candidate Attacks (not yet lab-fired)

- [ ] Re-run `webhooks/write` exfil with a **reachable** collector URL (e.g. a Consumption Function
      HTTP trigger) to confirm push-event payload exfil end-to-end + logs.
- [ ] Tag-poisoning / importImage on a private repo: confirm min perms and whether the overwrite is
      logged distinctly from a normal push.
