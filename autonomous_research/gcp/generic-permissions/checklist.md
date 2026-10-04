# Generic GCP permission patterns — open research

- [x] Separate policy-write authority from the roles/effects valid at each attachment point.
- [x] Separate generic create/update or `*ServiceAccount*` names from actual service-account
      attachment and execution primitives.
- [x] Correct `actAs` audit behavior to the current documented separate IAM Admin Activity record.
- [ ] Continue diffing new permission catalogs for `setIamPolicy`, `actAs`, token-signing and
      caller-selected identity fields, but promote a candidate only after a public method, exact
      prerequisites, useful impact and service-specific telemetry are established.
- [ ] When validating a newly supported attachment service, use a synthetic least-privilege account
      and benign identity proof, capture both resource and IAM audit entries, then delete the
      workload/account/bindings and restore any API or audit configuration.
