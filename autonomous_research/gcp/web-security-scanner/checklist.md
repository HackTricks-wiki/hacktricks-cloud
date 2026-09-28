# Web Security Scanner research checklist

## Completed 2026-09-28

- [x] Verify project-associated target restrictions and scan validation.
- [x] Verify input-only password versus returned username/login URL fields.
- [x] Reconcile every retained method with the current WSS audit catalog.
- [x] Add exact discovery, polling, result and target/application prerequisites.
- [x] Remove destructive scan blinding/stopping from post-exploitation.
- [x] Confirm documentation-only work made no cloud or application mutation.

## Safe future validation

- [ ] Against a disposable synthetic application, create one low-QPS custom scan under a minimum
      role, capture exact control-plane and target HTTP evidence, wait for completion, then delete the
      config and verify its child run/results no longer exist. Snapshot application data first and
      remove every scanner-created record.
- [ ] With Data Access enabled only for the fixture, read configuration/findings/paths using separate
      minimal principals and verify request-field redaction. Restore the exact audit policy.
- [ ] Test target validation only with harmless same-project and TEST-NET/out-of-scope URLs. A real
      cross-target or link-local acceptance failure is private-report material; never probe an
      unowned host.
