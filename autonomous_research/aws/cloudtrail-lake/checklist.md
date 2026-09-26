# CloudTrail Lake / cloudtrail-data — open ideas

- [x] PutAuditEvents channel poisoning — authz VERIFIED, documented (post-ex). See tested.md.
- [ ] **Channel resource-policy backdoor** — if an existing account HAS a Lake custom channel,
  `cloudtrail:PutResourcePolicy` on the channel could grant an attacker account `PutAuditEvents`
  (cross-account poisoning). Fits the cross-account resource-policy matrix — check whether the
  channel resource type is already enumerated there; add a row if not. (Lake closed to new
  customers, so lab-untestable.)
- [x] **EDS deletion / retention tamper** — DONE, authz VERIFIED, documented (post-ex, new
  subsection "Destroy or shrink a CloudTrail Lake event data store"). See tested.md. Retention-shrink
  = immediate/irreversible purge (no restore); delete = needs termination-protection cleared first +
  7-day PENDING_DELETION restore grace. Distinct from the trail-level StopLogging/DeleteTrail family
  because the EDS is a separate managed store.
