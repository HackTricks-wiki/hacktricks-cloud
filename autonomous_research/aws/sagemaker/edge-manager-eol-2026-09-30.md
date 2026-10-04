# SageMaker Edge Manager end-of-life audit — 2026-09-30

## Result

SageMaker Edge Manager is a reasoned exclusion from new HackTricks attack coverage. AWS ended the service on April 26, 2024, deleted all Edge Manager-held references to fleets, devices and packaging jobs, and states that applications calling Edge Manager APIs no longer work. Current live probes matched that retired state. No resource was created and no private vulnerability report was opened.

## Current model versus service state

The current AWS CLI still ships two historical models:

- SageMaker control-plane actions such as `ListDeviceFleets`, `ListEdgePackagingJobs`, and `ListEdgeDeploymentPlans`.
- The `sagemaker-edge` `2020-09-23` runtime with `GetDeviceRegistration`, `GetDeployments`, and `SendHeartbeat`.

The runtime model would historically expose device registration strings, model deployment S3 URLs/checksums and accept device heartbeat/deployment-result telemetry. That model is not evidence that the service remains available. AWS's explicit EOL page takes precedence.

## Live probes

Only inert reads with synthetic names were sent:

- `GetDeviceRegistration` could not connect to `edge.sagemaker.us-east-1.amazonaws.com` or `edge.sagemaker.eu-west-1.amazonaws.com`; the latter was repeated with a five-second connection timeout.
- `ListDeviceFleets`, `ListEdgePackagingJobs`, and `ListEdgeDeploymentPlans` returned terminal `ThrottlingException: Rate exceeded` in both allowed Regions. Repeating `eu-west-1` with `AWS_MAX_ATTEMPTS=1` confirmed that this was the service response rather than a useful paginated inventory.
- No create, update, register, deployment, heartbeat or delete operation was called.

These results are consistent with an intentionally dead control plane, not an authorization bypass or recoverable inventory path.

## Residual-resource boundary

AWS documents that resources created around Edge Manager can outlive the service, including:

- model packages/artifacts in customer S3 buckets;
- AWS IoT things, certificates and role aliases named like `SageMaker AIEdge-<fleet>`;
- IAM roles;
- Greengrass components named like `SageMaker AIEdge (<packaging-job>)`.

Those resources must be enumerated, secured and deleted through S3, IoT Core, IAM and Greengrass APIs. They do not make `sagemaker-edge` operational and should use the existing HackTricks coverage for those live services.

## Disposition

| Candidate | Disposition |
| --- | --- |
| Steal `DeviceRegistration` | Impossible to validate/use because the runtime endpoint is gone; do not publish stale technique |
| Recover deployment S3 URLs through `GetDeployments` | Runtime endpoint gone; enumerate S3/Greengrass directly instead |
| Forge `SendHeartbeat` device/model status | Retired endpoint; no active state to corrupt |
| Re-register devices or mutate edge plans | AWS says fleet/device/package references were deleted and management APIs no longer work |
| Residual IoT role alias / Greengrass component takeover | Still potentially relevant, but it is an IoT/Greengrass/IAM technique rather than SageMaker Edge Runtime; existing coverage applies |

## Cleanup

All calls were read-only or inert synthetic-name runtime reads. No Edge Manager, SageMaker, S3, IoT, Greengrass, IAM, CloudWatch or network resource was created. There is no temporary AWS infrastructure to delete.
