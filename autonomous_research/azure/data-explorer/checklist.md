# Data Explorer (Kusto/ADX) — Candidate Attacks (not yet lab-fired)

Cost note: even Dev/no-SLA ADX clusters run continuously — likely OVER the $5/30min gate. Verify the
Dev SKU hourly cost before provisioning; prefer to keep DOC-ONLY unless a cheap window exists.

- [ ] If a cheap cluster window exists: live-fire `.add database admins` data-plane self-grant and
      confirm it does NOT appear in Activity Log (control-plane blind spot).
- [ ] Test the python()/R plugin sandbox for egress/escape (UNVERIFIED) — stay in client infra; any
      host escape is a 0day.
- [ ] Confirm continuous-export to an attacker Storage account as standing exfil persistence.
