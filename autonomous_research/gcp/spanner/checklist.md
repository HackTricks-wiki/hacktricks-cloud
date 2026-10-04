# Spanner privilege-escalation checklist

## Completed

- [x] Separate instance, database, backup, database-role and project IAM resource boundaries.
- [x] Reconcile predefined role contents with current local role metadata.
- [x] Validate stable gcloud syntax for IAM binding, backup create/copy, restore, DDL and FGAC query.
- [x] Verify exact audit methods, permission types, defaults and LRO behavior.
- [x] Bound backup restore to a new compatible database and point-in-time contents.
- [x] Reject the nonexistent `spanner.databases.export` permission/confused-deputy claim.
- [x] Remove destructive-only and denial-of-service material from the privesc page.
- [x] Add minimum prerequisites, bounded impact, categorical stealth and log table to every H3.

## Safe future validation

- [ ] In an isolated, disposable low-capacity instance, grant a custom principal only `spanner.backups.copy` on a synthetic source backup and verify that copying to its own project needs no source row-read permission. Delete the restored database, copied backup, source backup and instance immediately after the test.
- [ ] In a synthetic FGAC database, combine a condition-scoped database-role assignment with a custom role containing only `spanner.databases.updateDdl`; verify role expansion and capture the exact start/completion audit pair, then revoke the DDL grant and delete the database.
- [ ] Capture LRO logs for cross-project `CopyBackup` and confirm the monitored-resource placement and authorization fields in both projects without generalizing beyond the observed API version.
- [ ] Test VPC Service Controls and relevant organization-policy behavior separately; do not present those controls as IAM permissions or as guaranteed blockers without a controlled perimeter test.

## Independent cross-review

- [x] Verify condition-safe IAM helper behavior and require an explicit unconditional condition.
- [x] Reconcile copy/restore caller permissions with source/destination resource placement.
- [x] Reconcile inherited encryption defaults, CMEK key-version availability and service-agent authorization without assigning cryptographic permissions to the caller.
- [x] Bound restore compatibility by project, instance configuration, and minimum-restorable edition.
- [x] Verify restored data/schema, IAM, FGAC database-role and excluded-data boundaries.
- [x] Verify LRO placement, start/completion caveats, exact audit methods and default visibility.
- [x] Confirm that FGAC role expansion crosses a data authorization boundary only for a deliberately separated custom IAM role plus an already usable condition-scoped database role.
