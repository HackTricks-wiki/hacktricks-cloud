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

- [ ] Extend the HNS ABAC differential beyond direct reads/listing to rename/move, batch, copy-from-URL,
      and `runAsSuperUser` paths. Use separate allow/deny canaries and condition every DataAction present
      in the test role; an operation that reaches a denied source or destination is a private-report
      candidate. The basic Blob-vs-DFS read/list matrix is already refuted in `tests-done.md`.
- [ ] Test whether path-conditioned user-delegation SAS remains constrained identically across Blob and
      DFS routes, including after the delegating assignment is narrowed or removed. Keep ordinary RBAC
      propagation delay separate from a token that survives beyond documented authorization behavior.
