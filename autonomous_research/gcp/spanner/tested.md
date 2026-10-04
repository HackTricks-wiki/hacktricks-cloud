# Spanner privilege-escalation research

## 2026-09-28 — current documentation and local CLI audit

No cloud resource was created, changed, or deleted. The review used current official Spanner IAM, backup/restore, FGAC, REST/audit documentation and stable local `gcloud` help.

### Retained primitives

- Resource IAM self-grant: `spanner.databases.setIamPolicy` can grant a database data role, while `spanner.instances.setIamPolicy` can grant a role inherited by databases in the instance. The raw API minimum is the set permission; the condition-safe gcloud helper also reads the policy.
- Backup recovery exfiltration: backup Writer/Admin authority has no row-read permission, but `spanner.backups.copy` on a victim backup plus `spanner.backups.create` in an attacker destination can move a backup cross-project. Destination `spanner.backups.restoreDatabase` plus `spanner.databases.create` restores it, and independent destination data access exposes the rows. Optional source backup creation additionally checks `spanner.backups.create` on the instance and `spanner.databases.createBackup` on the database.
- FGAC role expansion: `spanner.databases.updateDdl` can issue `GRANT` statements against database roles. It is a privilege escalation only when a custom role separates this permission from coarse data access and the attacker can already assume the restricted database role.

### Material corrections and rejected hypotheses

- Rejected `spanner.databases.export`: no such current IAM permission exists. The documented Dataflow export path runs under a Dataflow worker identity that needs actual Spanner read access; it is not a Spanner backup-style confused deputy.
- Removed instance/database deletion, drop-protection changes, scaling, edition downgrade and cost amplification. These are destructive or denial-of-service operations, not privilege escalation.
- Folded duplicate backup-create and restore headings into one permission-branched chain. An existing backup avoids `CreateBackup`; a cross-project restore requires `CopyBackup` into the destination project before `RestoreDatabase`.
- Corrected restore semantics: source IAM does not move to the new database; destination-instance inheritance applies. The restored snapshot also omits change-stream internal data, TTL row- deletion policies and split points.
- Corrected predefined-role bounds. Backup Writer/Admin contain no row-read permissions; Restore Admin contains no row-read permission. Conversely, predefined Database User/Admin holders with `updateDdl`, and Database Admin/Admin/Owner holders with policy authority, already have broad row access; the corresponding no-data starting points require custom-role separation.
- Corrected telemetry to fully qualified RPC names and current classes. `CreateBackup`, `CopyBackup`, `RestoreDatabase`, and `UpdateDatabaseDdl` are Admin Activity LROs. `SetIamPolicy` is Admin Activity but not an LRO. Operation polling and policy reads are `ADMIN_READ` Data Access; row methods are `DATA_READ`/`DATA_WRITE` Data Access. Data Access logs are disabled by default but can be enabled by inherited audit configuration.
- Bounded CMEK prerequisites: the source key version must remain available, the Spanner service agent needs `roles/cloudkms.cryptoKeyEncrypterDecrypter`, and keys selected for the destination must cover its regions. Conditional KMS `Decrypt`/`Encrypt` calls are Data Access in the key project.

### Local command validation

- Stable `gcloud spanner backups create` accepts `--retention-period=6h --async`.
- Stable `gcloud spanner backups copy` accepts fully qualified cross-project source and destination backup names; a copied backup has a minimum six-hour retention.
- Stable `gcloud spanner databases restore` accepts fully qualified source backup and destination database names and restores only into a new database.
- Stable `gcloud spanner databases ddl update` accepts semicolon-separated DDL and `--async`.
- Stable `gcloud spanner databases execute-sql` supports `--database-role`.

### Evidence limits

- No costly backup/restore LRO was run. Permission pairs, destination placement and audit behavior are taken from the current official API audit catalog and backup/restore documentation.
- No claim is made that a source policy, source IAM condition or later write is copied. The retained impact is limited to schema/data at the backup version time and destination-side access.

## 2026-09-28 — independent cross-review

- Confirmed all three retained H3s against the current REST method contracts, audit catalog, backup/CMEK documentation, FGAC guide, current predefined-role metadata, and local stable `gcloud` help. No cloud call or resource mutation was performed.
- Corrected both IAM helper examples to use `--condition=None`. This makes the intended unconditional grant explicit and lets the helper safely update a policy that already contains conditional bindings; the helper still requires the matching `getIamPolicy`, preserves policy version 3 and uses the returned `etag`.
- Corrected copy/restore encryption semantics: omitting encryption flags inherits the source backup's encryption configuration rather than assuming Google-managed encryption. CMEK key and key-version availability, Spanner service-agent access, and destination-region key coverage are service-side prerequisites, not direct KMS permissions required from the caller.
- Tightened restore bounds to a new database in the same project and instance configuration as the copied backup, with an edition satisfying the backup's minimum-restorable edition/features.
- Kept `updateDdl` as a genuine but narrow escalation. The DDL API is authorized by IAM rather than by the selected FGAC role, so a custom role can enlarge a restricted role the caller can assume; predefined Database User/Admin already have coarse data access and are not escalation starts.
- Kept the audit distinction that only `CreateBackup` and `RestoreDatabase` are explicitly documented as having completion entries without authentication/authorization information. The copy LRO belongs to the destination backup, but this does not justify claiming absence of any source-side telemetry.
