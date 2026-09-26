# MSK cross-account Replicator claim — negative, 2026-09-26

The book asserted that `kafka:CreateReplicator` plus `iam:PassRole` could copy a victim MSK cluster to an attacker-owned MSK cluster in a **different AWS account**. Current [AWS MSK supported-configuration documentation](https://docs.aws.amazon.com/msk/latest/developerguide/msk-replicator-supported-configs.html) explicitly requires both MSK clusters to be in the **same account** and says cross-account MSK Replicator is unsupported. [AWS's migration guide](https://docs.aws.amazon.com/msk/latest/developerguide/migration.html) points to Apache MirrorMaker 2.0 for cross-account replication. The previous IAM authorization test showed only that a malformed/partial `CreateReplicator` request passed its own action check and reached an `iam:PassRole` denial; it did not prove cross-account replication. Removed the unsupported attack section from the book instead of reframing it as a weak same-account copy.

The adjacent `PutClusterPolicy` technique had another material omission: its example named only the cluster ARN while claiming topic/group data access. [AWS's cross-account cluster-policy example](https://docs.aws.amazon.com/msk/latest/developerguide/mvpc-cross-account-permissions.html) includes cluster, topic, and group resource ARNs, and requires the current policy version when updating an existing policy. Corrected the example and prerequisites, plus persistence scope and stealth. Its previously reported `NotFoundException` probe is an IAM-gate test only, not an end-to-end external Kafka client test.

| Candidate | Result | Next action |
| --- | --- | --- |
| `CreateReplicator` to a foreign-account MSK target | Negative per current AWS service constraint | Keep out of book; revisit only if AWS adds cross-account support |
| Same-account Replicator to an attacker-accessible cluster | Possible but requires an accessible same-account target and additional setup; no distinct clean exfil under the original minimum permission | Keep as research candidate, not book technique |
| `PutClusterPolicy` cross-account cluster/topic/group grant | Supported by AWS documentation; existing IAM-gate probe only | Verify end-to-end on a suitable low-cost cluster if one becomes available |

No MSK infrastructure was launched in this audit.
