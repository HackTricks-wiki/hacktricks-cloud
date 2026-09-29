# AWS PCS attack ideas

- [x] Cluster shared-auth secret discovery and retrieval: documented `GetCluster` plus exact
  `GetSecretValue`, network prerequisites, scheduler impersonation impact and telemetry.
- [x] Slurm REST JWT signing-key theft: documented offline arbitrary-identity token minting and REST
  prerequisites.
- [ ] `RegisterComputeNodeGroupInstance`: test whether registration material is sufficiently bound
  to the intended EC2 instance, node group, account and Region; use a disposable zero-capacity group.
- [ ] `UpdateComputeNodeGroup`: verify launch-template/version and instance-profile repointing with
  exact `iam:PassRole`, and whether an existing queue can trigger the replacement automatically.
