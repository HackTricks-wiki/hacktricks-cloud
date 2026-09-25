# Storage — Candidate Attacks (not yet lab-fired)

Verify-first sweep (2026-09-25): all previously-listed items are ALREADY documented+lab-verified —
removed to prevent duplicate work (per the no-duplicates loop contract):
- Wildcard-CORS browser exfil → `az-storage-persistence.md` §"Wildcard CORS rule" (lab-verified:
  OPTIONS preflight returns `Access-Control-Allow-Origin: <arbitrary origin>` + `Allow-Credentials: true`).
- Disable versioning/soft-delete/change-feed → irrecoverable destruction is covered in
  `az-blob-storage-post-exploitation.md` (soft-delete/versioning/change-feed all disabled = permanent loss,
  ransomware payload step) and `az-storage-persistence.md` (object-replication + soft-delete sections);
  the `storageAccounts/write` / `blobServices/write` control-plane logging is documented.
- Storage Tasks MI-backed recurrence + logs → fully documented in `az-storage-tasks-post-exploitation.md`.

(none open — refill with new REAL candidates if/when identified.)
