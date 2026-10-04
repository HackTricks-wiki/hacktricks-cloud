# Bare Metal Solution research checklist

## Completed in the 2026-09-28 documentation audit

- [x] Reconcile SSH-key resource registration, serial-console authentication, and server-login key installation.
- [x] Verify supported serial-console firmware, command, endpoint, and permission boundaries.
- [x] Inspect the current v2 discovery schemas for instance authentication information, NFS allowed clients, snapshots, volumes, and LUNs.
- [x] Inspect stable/alpha gcloud help and the NFS update implementation for helper-only permissions.
- [x] Reconcile BMS and KMS audit methods, permission types, defaults, and operation boundaries.
- [x] Reconcile the standard `loginInfo`/Secret Manager password path with the optional Preview `LoadInstanceAuthInfo`/CMEK path, including direct-secret versus service-account impersonation.
- [x] Remove destructive, availability-only, generic host, and unsupported offline-copy claims.
- [x] Confirm that no cloud state was mutated during this pass.

## Safe future validation in a purpose-built BMS lab

- [ ] With a disposable encrypted-password BMS server, test whether `baremetalsolution.instances.loadAuthInfo` is currently custom-role grantable and identify every predefined role that actually includes it. Do not infer this from `instances.*` display grouping.
- [ ] Retrieve a disposable standard `customeradmin` initial credential through `loginInfo` using separately scoped principals for direct secret access and service-account impersonation. Verify the first-login rotation prompt and correlate BMS, IAM Credentials, Secret Manager, host, and network telemetry.
- [ ] Retrieve and decrypt a disposable Preview CMEK initial password, verify `root` versus `customeradmin` local-login behavior before and after password rotation, inspect exact response redaction, and correlate BMS/KMS audit entries. Remove local plaintext and ciphertext immediately.
- [ ] Add a temporary read-only `/32` NFS allowed client in a test share, compare raw PATCH against the gcloud helper, capture the operation/audit behavior, restore the exact prior allowed-client list, unmount the export, and verify cleanup.
- [ ] Determine whether interactive serial-console connection/disconnection produces any gateway audit or platform log outside `baremetalsolution.googleapis.com`; do not claim absence based only on the BMS API catalog.
- [ ] Revisit volume-attachment data access only if Google publishes a callable v2 attach method and exact authorization contract. Do not extrapolate from permission names or console UI.
- [ ] Recheck whether the audit catalog's non-LRO classification for `UpdateNfsShare` changes to match the operation-returning API.

These tests require paid, pre-provisioned BMS resources and customer-network access. They must not be attempted in a general lab merely to create evidence, and every allowed-client, mount, key, local credential file, and other test artifact must be removed after an authorized test.
