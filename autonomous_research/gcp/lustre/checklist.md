# Managed Lustre research checklist

## Completed 2026-09-28

- [x] Separate instance enumeration from privilege escalation.
- [x] Separate standalone file-system export, attacker-controlled import, and deletion from privesc.
- [x] Retain only the two-transfer chain that exercises a stronger source-bucket grant held by the
      transfer service agent.
- [x] Bound the result to Cloud Storage data access; do not claim token or general SA takeover.
- [x] Correct ImportData/ExportData to Data Access LROs disabled by default.
- [x] Verify current GA gcloud flags and LRO polling permission.
- [x] Record source/destination bucket roles, capacity/path, concurrency, and VPC-SC prerequisites.

## Open bounded leads

- [ ] In a disposable no-sensitive-data project, test the exact authorization check for a
      caller-selected transfer service account and whether cross-project service accounts are
      accepted. Do not claim `iam.serviceAccounts.actAs` as service-specific fact until verified.
- [ ] Test whether a prefix-limited service-agent bucket grant and a matching import URI remain
      prefix-bounded under hierarchical namespace and managed-folder IAM.
- [ ] Verify the exact operation-poll audit behavior if Google adds operations helpers to the Managed
      Lustre audit catalog.
- [ ] Reassess IP access-rule updates as post-exploitation access to the mount, not privesc, unless a
      future API change also grants a new cloud identity or authorization.
