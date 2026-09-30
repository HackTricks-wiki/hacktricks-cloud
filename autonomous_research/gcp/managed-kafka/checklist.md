# Managed Kafka post-exploitation - checklist

## Completed 2026-09-28

- [x] Reconcile SASL, mTLS, IAM connection permission, Kafka ACLs, and the `allow.everyone.if.no.acl.found` default.
- [x] Verify consume/produce minimum prerequisites and bound access to ACL-authorized topics/groups.
- [x] Reconcile `AuthenticateConnection` Data Access logging with the absence of per-message audit logs.
- [x] Add automatic broker/topic Monitoring metrics as downstream detection signals.
- [x] Verify connector create/update permissions, curated plugins, service-agent source/sink access, Connect logs, and Pub/Sub message-audit behavior.
- [x] Verify the Connect-project service-agent ACL principal and cross-project primary-cluster IAM boundary.
- [x] Correct topic configuration permissions and retention/deletion semantics.
- [x] Verify consumer-group inactive prerequisite, inline topics schema, offset-reset bounds, and audit methods.
- [x] Add the service-agent topic/group `READ` ACL prerequisite for control-plane offset updates.
- [x] Verify Schema Registry soft/permanent deletion, exact permissions/methods, references/read-only constraints, and Preview status.
- [x] Remove standalone cluster deletion and false schema-version poisoning claims.
- [x] Validate current gcloud commands and generated v1 Schema Registry paths against SDK 586.0.0.
- [x] Verify exact broker/topic/Connect metric descriptor names and correct Schema Registry `ListSchemaVersions` audit method.
- [x] Remove the unproven generic Connect-secret read oracle and the misclassified stolen-token/topic
      credential heading from privilege escalation.

## Safe future tests

- [ ] In a disposable no-production-data cluster, compare `Auth.AuthenticateConnection` entries with Data Access disabled/enabled and determine whether a single Kafka client produces one event per broker connection or token refresh. Clean up the cluster immediately.
- [ ] With bounded ACL fixtures, verify the exact ACL evaluation when literal, prefixed, and all-resource patterns overlap and no ACL exists for one of the producer/consumer resources.
- [ ] Compare control-plane topic update/delete with `kafka-configs.sh` and `kafka-topics.sh`, confirming that broker-protocol mutations lack the corresponding Admin Activity method while Monitoring metrics still change.
- [ ] Validate the exact Kafka ACL operations required by direct broker-based consumer-group offset alteration and deletion before documenting that alternative path.
- [ ] Test a cross-project Pub/Sub sink owned by the tester, grant only `pubsub.topics.publish` to the Connect-project service agent, confirm connector logs/metrics and absence of Pub/Sub Publish audit records, then delete the connector and destination topic.
- [ ] In a disposable Preview Schema Registry, verify soft versus permanent deletion, read-only/reference failures, client cache behavior, and exact `permanent` query handling; delete the registry afterward.
- [ ] Resolve the current official-documentation conflict for version hard delete: stable v1 discovery/REST/local SDK use `/v1` plus `permanent=true`, while the 2026-09-24 product guide shows `/v1main` plus `hardDelete=true`. Use only a disposable soft-deleted version and record both non-mutating error behavior and the successful contract before cleanup.
- [ ] With synthetic secrets and each currently curated connector plugin, test whether any documented
      configuration can cause an arbitrary mounted secret value—not merely its file path or intended
      authentication use—to be returned or published to an attacker-readable destination. Delete the
      Connect cluster, connector, secret/version, topics, destination and every temporary grant.
