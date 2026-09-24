# Firestore Datastore — open ideas

Open ideas — Firestore / Datastore.

- [ ] **Verify `datastore.indexes.*` vs `datastore.schemas.*` permission naming.** Check current IAM
  catalog (`gcloud iam list-testable-permissions //datastore.googleapis.com/...` or role describe) and
  correct any wiki page that cites a stale `datastore.indexes.*` gate. Verification-only.
- [ ] **(organizational)** Consider whether Firestore's userCreds/clone/import-export warrant lifting
  from the enum page into proper privesc/persistence pages for parity — only if it improves clarity,
  not as duplicate content.
