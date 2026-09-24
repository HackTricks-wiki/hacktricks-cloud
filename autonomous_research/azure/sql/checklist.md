# Azure SQL — Candidate Attacks (not yet lab-fired)

Blocked by lab wall (no logical-server provisioning + no outbound 1433). Re-attempt only if the wall
lifts, or via a Managed Instance if one becomes cheaply available.

- [ ] If provisioning unlocks: confirm `##MS_LoginManager##` self-service login creation as a min-priv
      server principal, and whether it appears in the SQL audit vs Activity Log.
- [ ] Confirm `failoverGroups` continuous exfil to an attacker-administered server in the same tenant
      produces NO read event on the victim (the key stealth claim).
- [ ] Test `encryptionProtector/write` TDE-repoint to an attacker KV key as a ransomware kill-switch.
