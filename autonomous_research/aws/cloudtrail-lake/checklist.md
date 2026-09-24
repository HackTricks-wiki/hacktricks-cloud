# CloudTrail Lake / cloudtrail-data — open ideas

- [x] PutAuditEvents channel poisoning — authz VERIFIED, documented (post-ex). See tested.md.
- [ ] **Channel resource-policy backdoor** — if an existing account HAS a Lake custom channel,
  `cloudtrail:PutResourcePolicy` on the channel could grant an attacker account `PutAuditEvents`
  (cross-account poisoning). Fits the cross-account resource-policy matrix — check whether the
  channel resource type is already enumerated there; add a row if not. (Lake closed to new
  customers, so lab-untestable.)
- [ ] **EDS deletion / retention tamper** — `cloudtrail:DeleteEventDataStore` /
  `UpdateEventDataStore --retention-period` to shrink/destroy the Lake investigation history
  (anti-forensics). Termination protection + 7-day wait may apply. Compare to the existing
  StopLogging/DeleteTrail tamper coverage before documenting.
