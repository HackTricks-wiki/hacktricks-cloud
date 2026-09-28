# Filestore research checklist

## Completed

- [x] Audit every post-exploitation H3 against the no-garbage bar.
- [x] Separate Filestore management-plane IAM from NFS data-plane authorization.
- [x] Record exact raw-API versus current `gcloud` helper/polling permissions.
- [x] Replace destructive in-place restore with non-destructive create-from-backup cloning.
- [x] Correct NFS export defaults and `anon_uid` / `anon_gid` validation.
- [x] Add bounded impact, categorical stealth, and current audit class/default tables to every H3.
- [x] Record that no cloud resource was mutated and no cleanup was necessary.
- [x] Reciprocal-review NFSv3/NFSv4.1 mount prerequisites and make backup-to-clone LRO sequencing executable.

## Follow-up validation ideas

- [ ] With prior approval, test `file.instances.createCrossProjectBackup` using a tiny disposable
  source share and attacker-owned destination project. Capture which project receives
  `CreateBackup`, every secondary permission check, and whether a current supported client can
  express the cross-project source. Delete the destination backup immediately and confirm no source
  mutation; do not run this without the exact cost/cleanup plan approved first.
- [ ] With prior approval, grant a custom role containing only `file.backups.useReadOnly` on a
  disposable backup and `file.instances.create` on a clean target project, then confirm the precise
  create-from-backup authorization boundary and delete the clone immediately.
- [ ] Capture one `UpdateInstance` LRO with a synthetic reversible export rule and restore the exact
  prior rule set, confirming which NFS fields appear in Admin Activity request metadata.

All future live tests must use synthetic data, minimum permissions, bounded cost, pre-recorded
rollback, immediate teardown, and post-cleanup inventory confirmation.
