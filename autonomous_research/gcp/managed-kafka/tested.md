# Managed Kafka post-exploitation - tested research

## 2026-09-28 - official documentation and local CLI/source audit

No cloud resources were created or mutated. The page was audited against current Google Cloud product, REST/RPC, IAM, audit-logging, monitoring, Kafka ACL, Kafka Connect, and Schema Registry documentation plus Google Cloud CLI 586.0.0 help and generated v1 client source.

### Retained

- **Broker consumption:** SASL requires `managedkafka.clusters.connect`, network reachability, and effective Kafka `READ` authorization on the topic and consumer group. mTLS uses certificate identity and ACLs without `clusters.connect`. Impact is bounded to authorized, retained records.
- **Broker injection:** SASL connection plus Kafka producer authorization can inject records. Existing topics require `WRITE`; automatic topic creation additionally requires `CREATE`, and transactional producers also require transactional-ID `WRITE`.
- **Kafka Connect sink exfiltration:** connector create/update is a server-side exfiltration route with a different permission boundary from direct broker access. It requires an existing Connect cluster, source read authorization for the Managed Kafka service agent, and destination write access. An attacker-controlled Pub/Sub project can grant its own topic to the victim Connect-project service agent.
- **Targeted topic destruction:** control-plane topic update/delete and equivalent broker-admin paths were retained. The Google API needs `topics.update`/`topics.delete`; it does not use Schema Registry's `config.update`. Retention expiry is segment-based and asynchronous.
- **Consumer-group offset tampering:** update requires an inactive group and explicit per-partition offsets. Deletion removes offsets but restart behavior depends on client `auto.offset.reset`.
- **Schema deletion:** soft/hard subject or version deletion can disrupt clients that fetch the schema. Permanent deletion requires a prior soft delete; references/read-only mode can block deletion.

### Corrected or rejected

- Rejected the claim that `managedkafka.clusters.connect` grants universal read/write access. Kafka ACLs authorize operations; open access exists only where no ACL matches.
- Corrected the blanket “no audit log” claim. SASL authentication maps to `google.cloud.managedkafka.v1.Auth.AuthenticateConnection`, a `DATA_WRITE` Data Access event disabled by default. Individual produce/fetch operations are not audited.
- Rejected raw access-token-as-OAUTHBEARER-secret guidance. The documented direct token example uses SASL/PLAIN; OAUTHBEARER requires Google's callback handler/local auth server.
- Removed `connectors.update` as a prerequisite for connector creation. Create and update are alternative permissions for their corresponding operations.
- Corrected sink telemetry: Connect cluster logs and connector metrics are exported; Pub/Sub currently writes no Data Access logs for Publish/Subscribe/Acknowledge message operations.
- Bounded the connector identity to the Connect-project Managed Kafka service agent, including its `User:service-...` Kafka ACL principal and the pre-existing cross-project `roles/managedkafka.serviceAgent` attachment requirement when the primary Kafka cluster is in another project.
- Corrected topic configuration permissions from false `managedkafka.config.update/delete` claims to `managedkafka.topics.update`; `config.*` belongs to Schema Registry configuration.
- Rejected “near-zero retention immediately wipes data.” Retention deletes completed segments asynchronously.
- Bounded consumer-group deletion: it removes committed offsets but does not deterministically choose replay versus skip.
- Added the missing control-plane offset-update prerequisite: the cluster service agent needs Kafka `READ` authorization on both the topic and consumer group when applicable ACLs exist; Google documents the `User:__AUTH_TOKEN__service-...` ACL principal for this API workflow.
- Rejected `managedkafka.versions.checkCompatibility` as a prerequisite for `versions.create`; compatibility enforcement is server-side. A new version alone does not force clients to use it.
- Removed standalone cluster deletion as a low-value, obvious destructive action. It is a cluster DoS, not a distinct post-exploitation primitive, and it does not delete separate Connect clusters.

### Telemetry verified

- `CreateConnector`, `UpdateConnector`, `UpdateTopic`, `DeleteTopic`, `UpdateConsumerGroup`, `DeleteConsumerGroup`, `DeleteVersion`, and `DeleteSubject` are `ADMIN_WRITE` Admin Activity and logged by default. None of these retained methods is an LRO.
- `AuthenticateConnection` is `DATA_WRITE` Data Access; control-plane get/list and Schema Registry reads are `ADMIN_READ` Data Access. Data Access is disabled by default.
- Managed Kafka does not emit per-message produce/fetch Cloud Audit Logs. Automatically collected cluster/topic metrics expose aggregate request, message, byte, offset, and error changes.
- Broker-admin changes made through the Kafka protocol do not emit the corresponding Google control-plane `UpdateTopic`/`DeleteTopic` audit method.
- Corrected the Schema Registry read method from nonexistent `ListVersions` to `ListSchemaVersions`.
- Confirmed that the stable v1 REST discovery document, published v1 REST reference, and local SDK 586.0.0 all use `/v1/...` with `permanent=true` for hard version deletion. A newer product guide currently shows `/v1main/...` with `hardDelete=true`; this documentation conflict remains a bounded live-validation lead rather than changing the page away from the published API contract.

### Local command/source checks

- Stable `gcloud managed-kafka connectors create`, topics update/delete, consumer-groups update/delete, and clusters describe syntax checked with SDK 586.0.0 help.
- Generated v1 Schema Registry client uses `/v1/.../versions` and the `permanent` query parameter; the local client confirms a soft delete must precede permanent deletion.
- Metric descriptor names were checked against the Cloud Monitoring catalog, including Connect sink record/byte/task metrics and topic offset/size/request/error metrics.

## 2026-09-28 — privilege-escalation deduplication

- Removed both prior privilege-escalation H3s. Managed Kafka resources expose no resource `setIamPolicy`, caller-selectable runtime service account or credential-minting method.
- Demoted the Connect-secret proposal to a controlled test lead. The service agent must already be authorized for each exact secret version; the worker mounts it read-only; and the caller receives only a path/config-provider expression. The old page did not establish a supported curated plugin that reliably emits an arbitrary substituted secret, so it overstated a general read oracle.
- Reclassified stolen broker-token and topic-borne credential material. Token theft is a prior identity compromise; broker use remains bounded by network and Kafka ACLs; topic reads are already documented post-exploitation rather than as cloud privilege escalation.
- This pass used current official access-control, RPC, Connect-secret and authentication references only. It did not call a cloud API, read a cluster, mount a secret or change any resource.

## 2026-09-28 — reciprocal review

- Independently rechecked the no-primitive conclusion against the current Managed Kafka v1 RPC surface, access-control contract, Connect secret-mount model, curated connector boundary and local SDK 586.0.0 generated clients. No resource-level IAM policy method, caller-selected service account or credential-minting method was found, so no additional privilege-escalation H3 was restored.
- Reconfirmed that a mounted Secret Manager version is exposed to a worker as a read-only file and referenced through the config provider; that alone does not prove a supported connector can emit an arbitrary value. The synthetic-plugin matrix remains the correct bounded test lead.
- No cloud API was called and no cluster, Connect resource, secret, ACL or IAM policy was accessed or changed during this review.
