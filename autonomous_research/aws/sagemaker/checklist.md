# SageMaker research checklist

## Closed in the 2026-09-29 HyperPod pass

- [x] `UpdateClusterSoftware` custom-AMI replacement: useful existing-role root execution path;
  published with Slurm limitation and disruption telemetry.
- [x] Minimum action boundary: isolated caller with only `UpdateClusterSoftware` reached
  service-side cluster lookup for both default and custom-image request shapes.
- [x] Expensive live cluster fixture avoided; account inventory was empty in both allowed Regions.

## Open follow-ups

- [ ] On a future authorized disposable HyperPod cluster, confirm IMDS credential retrieval and
  exact CloudTrail request/response redaction for a canary-only execution role.
- [ ] Test whether `UpdateCluster` accepts a changed lifecycle S3 path for an existing group while
  retaining the existing execution role, and whether it immediately reprovisions/reruns nodes.
- [ ] Test the exact `iam:PassRole` evaluation when `UpdateCluster` repeats an unchanged execution
  role versus adding a new group or changing the role.
- [ ] Review automatic patch schedules and scheduler-config mutation for durable image replacement
  or rollback suppression beyond the one-shot update primitive.
