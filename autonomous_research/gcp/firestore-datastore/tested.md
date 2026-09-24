# Firestore Datastore — tested

Firestore / Datastore. Covered (delete-protection/PITR strip as evasion precursor; userCreds+clone+
import/export documented on the enum page). No per-database setIamPolicy permission exists (confirmed).

## Known structural note (not a knowledge gap)
- Firestore's userCreds/clone/import-export live on the ENUM page rather than dedicated privesc/
  persistence/post-ex pages — the DB-service outlier. Not reorganised.

## Standing item to verify
- `datastore.indexes.*` permission name may be stale (modern IAM may use `datastore.schemas.*`).
