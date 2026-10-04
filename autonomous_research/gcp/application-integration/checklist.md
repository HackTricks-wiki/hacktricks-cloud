# Application Integration — private-first regression frontier

## 2026-09-29 historical-vulnerability delta

- [x] Record GCP-2026-064 / CVE-2026-19759: an internal-only task type allowed an authenticated
      caller to execute arbitrary internal RPCs under a privileged identity before June 17, 2026.
- [x] Record GCP-2026-065 / CVE-2026-81867: crafted JavaScript Task input reached unsafe
      deserialization and arbitrary code execution on shared production servers before June 28,
      2026.
- [x] Record GCP-2026-066 / CVE-2026-81375: a crafted Email Task attachment path read and
      exfiltrated arbitrary Google-internal files before June 30, 2026.
- [x] Confirm the authorized lab has neither `integrations.googleapis.com` enabled nor an
      Application Integration service identity. Do not enable it solely for regression testing;
      repository/integration setup could leave a Google-managed identity after teardown.

## Safe regression matrix for an existing disposable fixture

- [ ] Test server-side allowlisting of task types across create, update, clone/import and deploy
      paths. Vary only documented serialization aliases, API versions and harmless task bodies. If
      an internal-only type is accepted, stop before invocation and keep the result private.
- [ ] Test Email Task attachment canonicalization with files created inside the owned fixture:
      separator variants, dot segments, encoded segments, URI schemes, archive-member syntax and
      link resolution. Never request a Google-internal or another tenant's file; a boundary failure
      can be proven with two owned directories.
- [ ] Test JavaScript Task deserialization using inert canary objects: nested typed values,
      prototype-like keys, cyclic/reference encodings and version clone/import round trips. Stop at
      a benign deterministic marker; do not run a reverse shell, access metadata or touch shared
      files.
- [ ] Compare draft validation, deployment validation and runtime decoding. A payload rejected in
      one stage but accepted after export/import, version copy or regional replay is private-first.
- [ ] Capture minimum `integrations.integrationVersions.*` and deployment/invocation permissions,
      exact Admin Activity/Data Access/platform logs and the executing identity for every stage.
- [ ] Delete versions, integrations, auth configs, triggers and local payloads; restore API/IAM
      state and verify no service identity or asset was newly materialized.

## Do not publish as current

- [ ] Do not present any of the three bulletins as a live technique without a current controlled
      reproduction and coordinated disclosure.
- [ ] Do not infer that ordinary JavaScript/Email Task authoring still escapes the managed sandbox.
- [ ] Do not probe internal RPC names, Google-internal paths, metadata endpoints or other tenants.
