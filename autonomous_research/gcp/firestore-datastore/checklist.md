# Firestore Datastore — open ideas

- [ ] **(organizational)** Consider whether Firestore's userCreds/clone/import-export warrant lifting
  from the enum page into proper privesc/persistence pages for parity — only if it improves clarity,
  not as duplicate content.

## Resolved (moved from open)

- [x] **`datastore.indexes.*` vs `datastore.schemas.*` naming** — RESOLVED 2026-09-24 via testable-perms
  dump. **BOTH families exist** in the live IAM catalog (`datastore.indexes.{create,delete,get,list,update}`
  AND `datastore.schemas.{create,delete,get,list,update}`). The wiki's `datastore.indexes.*` citation is
  **valid, not stale** — no correction needed. See tested.md.
