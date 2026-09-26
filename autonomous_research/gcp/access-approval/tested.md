# Access Approval — tested

## 2026-09-26 metadata and audit-method review

- Reconciled both post-exploitation techniques against Google's current Access Approval audit-method
  table. Settings update/delete and request approve/dismiss/invalidate are always-on Admin Activity;
  settings/request get/list methods produce no audit log at all.
- Added exact minimum permissions, categorical stealth ratings, and fully qualified method names to
  both existing technique tables. Removed the old caveat that method names were merely inferred.
- Documentation and read-only official-reference review only. No Access Approval setting or request
  was changed and no lab resource was created.
