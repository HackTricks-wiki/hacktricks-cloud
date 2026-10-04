# Cluster Director security research checklist

## Completed — 2026-09-29

- [x] Map Cluster, compute, storage, network and Slurm executable configuration fields.
- [x] Verify predefined roles, custom-role support, service-agent authority and current identity
      schema.
- [x] Test a raw login-node startup-script partial update with an exact update-only custom role.
- [x] Prove the retained `iam.serviceAccounts.actAs` check with negative and positive controls.
- [x] Prove root hook execution and use of the retained VM identity without direct token-mint or
      target Storage access.
- [x] Capture Cluster Director Admin Activity, full request content, LRO pairing, Compute
      reconciliation and the absence of default Storage Data Access.
- [x] Restore benign content and verify full zero-residue cleanup, including generated network/DNS
      resources and the service agent/API baseline.

## Safe live-validation frontier

- [ ] On a disposable cluster with a zero-count/dynamic node set, test
      `orchestrator.slurm.nodeSets[].computeInstance.startupScript` against both a newly created node
      and an existing node after it becomes idle. Preserve the complete repeated `nodeSets` value,
      verify the retained `actAs` check, and scale back to zero before deletion.
- [ ] Test Slurm prolog, epilog, task-prolog and task-epilog script updates with harmless markers.
      Determine the guest UID, environment/credential availability, trigger conditions and whether
      every hook update rechecks the retained account. Never submit a real workload or credential.
- [ ] Recheck whether a service-account field appears in a future stable discovery revision. If it
      does, test same-account retention and replacement separately; any replacement without target
      `actAs` is private-first vulnerability material.
- [ ] Compare v1, v1beta and CLI authorization parity for partial update masks and omitted sibling
      fields. Treat any version-specific `actAs` bypass as private-first and avoid a public book
      claim until reported.
- [ ] Test operation cancellation only with a benign script to determine whether a cancelled LRO can
      leave desired state changed but nodes unreconciled. Always restore a benign script and delete
      the full cluster dependency graph.
- [ ] Enable Storage Data Access only in a disposable project to capture payload attribution, then
      restore the exact prior audit policy. Correlate the initiating caller, service identities and
      retained VM account without retaining any token.

## Do not publish without stronger evidence

- [ ] No arbitrary service-account selection under the current API.
- [ ] No update-only/no-actAs route; live testing rejected it.
- [ ] No blanket claim that every executable Slurm hook runs as root or has metadata credentials;
      only the login-node startup hook is verified end to end.
- [ ] No 0-day label for documented update-plus-actAs execution.
