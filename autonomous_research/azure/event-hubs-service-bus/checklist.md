# Event Hubs / Service Bus — Candidate Attacks (not yet lab-fired)

- [ ] Self-minted SAS authorization-rule persistence: create a rogue `authorizationRules` with
      Listen+Send, confirm the SAS token keeps working after the creator's RBAC is removed, record logs.
- [ ] Confirm on **Service Bus**: `disableLocalAuth=true` lockout + `networkRuleSets` parity with EH.
- [ ] Test whether a covert consumer group is visible in any default diagnostic and how long it
      persists silently (stealth measurement).
- [ ] SB Geo-DR alias standing-access persistence — document without firing the irreversible break.
