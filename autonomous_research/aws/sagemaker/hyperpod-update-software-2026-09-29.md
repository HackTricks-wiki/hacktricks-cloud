# SageMaker HyperPod software-update audit — 2026-09-29

## Candidate and disposition

`UpdateClusterSoftware` accepts a same-account custom AMI and replaces the root volumes of selected
HyperPod instance groups. The nodes retain their configured execution role and AWS documents that
the operation reruns lifecycle scripts. This produces a clean existing-role code-execution path
without a role parameter or caller-side `iam:PassRole`. It is expected service functionality and is
published as a privilege-escalation technique, not a private vulnerability report.

## Documentation evidence and limits

- The authorization reference scopes `sagemaker:UpdateClusterSoftware` to a cluster resource and
  lists no dependent action for the operation.
- The custom AMI must be owned by the same account and satisfy HyperPod's current encryption and
  volume restrictions.
- Omitting the instance-group list patches every group.
- The update replaces root volumes, causes node downtime, does not drain workloads, and reruns the
  existing lifecycle scripts.
- Slurm cannot move from its default AMI to a custom AMI through this operation. Slurm
  custom-to-custom updates are supported; the documented EKS custom-image path is supported.
- Impact reaches the existing instance-group role only when the image's root code obtains the node
  role credentials; the role is not changed by the update.

## Safe authorization probe

No HyperPod clusters existed in `us-east-1` or `eu-west-1`, and creating one would require costly
managed nodes. A disposable IAM user was therefore granted only
`sagemaker:UpdateClusterSoftware` on `*`. Calls against a synthetic cluster name both without an
image and with `ami-0123456789abcdef0` reached SageMaker's `ResourceNotFound` response. The user had
no `iam:PassRole`, `ec2:*`, EKS, list, or describe permission. This proves the action gate reaches
service-side cluster lookup independently; acceptance of a real AMI remains bounded by the
documented image requirements.

A final probe scoped the same single action to the exact synthetic ARN
`arn:aws:sagemaker:us-east-1:228478051196:cluster/htpod0000001` and supplied that ARN plus the custom
image ID. It again reached SageMaker's cluster-not-found path, confirming cluster resource scoping
rather than requiring `Resource: "*"`.

## Telemetry

`UpdateClusterSoftware` is a SageMaker management event. Successful updates also emit HyperPod
cluster events for scheduling, patching start/completion, root-volume replacement and instance
patch success/failure. The control-plane event should be correlated with subsequent activity by the
affected instance-group role and, where applicable, earlier EC2 image/snapshot changes.

## Cleanup

The disposable access key, inline policy and IAM user were deleted after each probe. A
prefix-filtered IAM inventory returned empty. No cluster, node, AMI, snapshot, VPC, EKS, S3 or other
billable resource was created or modified.

## Sources

- https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_UpdateClusterSoftware.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/hyperpod-custom-ami-cluster-management.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-eks-operate-cli-command-update-cluster-software.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-prerequisites-iam.html
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-cluster-events-reference.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_sagemaker.html
