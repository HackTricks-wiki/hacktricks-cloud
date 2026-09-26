# Cloud Tasks — open ideas

- [ ] Revalidate audit behavior if Google changes the explicit `CreateTask` exclusion in its audit-logging reference. Use an existing test queue and enable Data Access logging only in a disposable lab context; restore the prior policy and remove test tasks.
- [ ] Recheck whether any newly released task operation exposes a distinct permission or execution path beyond the documented enqueue, replay, and queue-override families.
