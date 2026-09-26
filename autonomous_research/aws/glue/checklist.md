# Glue — open ideas

Glue already has privesc + post-exploitation coverage (catalog/job code-exec, DataAccessRole
confused-deputy, **GetConnection plaintext-credential harvest**). Only a dedicated **enum** page
under `aws-services/` is organizationally missing.

- [ ] **(organizational, low priority)** Dedicated enum page under `aws-services/` gathering the
  read-only recon surface (`GetDatabases`/`GetTables`/`GetConnections`/`GetJobs`/`GetDevEndpoints`,
  job `ScriptLocation` S3 reads). Not a new *technique* — the credential-disclosure vector is
  already in the post-exploitation page. Only worth doing if the enum section is desired for parity
  with other services; must NOT duplicate the post-ex GetConnection content.

## Resolved (moved from open)

- [x] **GetConnection password disclosure** — VERIFIED live 2026-09-24 and found ALREADY DOCUMENTED
  in `aws-glue-post-exploitation` (`## glue:GetConnection — plaintext connection credentials`).
  See tested.md. Not a gap.
