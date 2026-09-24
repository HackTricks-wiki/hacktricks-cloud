# Monitor — Candidate Attacks (not yet lab-fired)

- [ ] Live-fire `dataCollectionRules/write` to add an AMA file-collection rule that exfils a target
      file path from a monitored VM to attacker-readable logs; record min perms + logs.
- [ ] `dataCollectionRules/data/write` log forgery: inject fake events into a Log Analytics table to
      poison detections; confirm whether the injection is itself logged.
- [ ] Confirm which action-group receiver types (webhook/logic-app/automation) give the strongest
      unauth-callback pivot and their log footprint.
