# Cloud Tasks — open ideas

- [x] Validate the GA task-level retry override with `cloudtasks.tasks.create` but no queue-update permission, including persisted state and default audit visibility.
- [x] Validate v2 batch create/delete permission boundaries, limits, and default audit classification without allowing any task to dispatch.
- [x] Test outer-parent versus nested parent/name confusion for batch create/delete across two queue-level IAM boundaries; the service rejected cross-queue creation and preserved unauthorized deletion targets.
- [ ] Revalidate audit behavior if Google changes the explicit `CreateTask` exclusion in its audit-logging reference. Use an existing test queue and enable Data Access logging only in a disposable lab context; restore the prior policy and remove test tasks.
- [ ] Recheck whether any newly released task operation exposes a distinct permission or execution path beyond the documented enqueue, replay, and queue-override families.
- [ ] In a disposable queue with sampling enabled, compare per-item `TaskActivityLog` coverage for `BatchCreateTasks` and `BatchDeleteTasks`; do not enable project-wide Data Access logging and restore/delete the queue immediately.
