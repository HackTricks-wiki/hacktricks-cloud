# Database Migration Service — open questions

- [ ] With an existing authorized source profile and a controlled destination, live-test the exact minimum DMS and destination permissions for migration start and continuous promotion. Do not infer a cross-project data path from the service-agent role alone.
- [ ] Check whether a caller with `migrationJobs.create` can reference a source connection profile they cannot read, and whether DMS evaluates resource-level IAM on the profile. A successful unauthorized reference would be a potential boundary failure; do not publish without an isolated test.
