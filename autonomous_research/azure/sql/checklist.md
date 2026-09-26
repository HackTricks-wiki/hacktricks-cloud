# Azure SQL — Candidate Attacks (not yet lab-fired)

Blocked by lab wall (no logical-server provisioning + no outbound 1433). Re-attempt only if the wall
lifts, or via a Managed Instance if one becomes cheaply available.

- [ ] If provisioning unlocks: confirm `##MS_LoginManager##` self-service login creation as a min-priv
      server principal, and whether it appears in the SQL audit vs Activity Log.
- [ ] Confirm `failoverGroups` continuous exfil to an attacker-administered server in the same tenant
      produces NO read event on the victim (the key stealth claim).
- [ ] Test `encryptionProtector/write` TDE-repoint to an attacker KV key as a ransomware kill-switch.
- [ ] On a wholly disposable SQL database with disposable backups, validate the exact minimum actions and
      ordering for short-/long-term retention reduction, restore-point deletion, geo-backup disablement,
      and LTR time-based/legal-hold immutability removal. Keep this destructive theory out of the book
      until a safe end-to-end reproduction exists.
