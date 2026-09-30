# SageMaker Job Runtime / multi-turn RFT audit — 2026-09-30

## Result

Audited the new SageMaker model-customization jobs and `sagemakerjobruntime` API. Published a scoped post-exploitation technique for corrupting active AgentRFT trajectories and reward labels with `CompleteRollout` / `UpdateReward`, plus the missing enumeration and telemetry model. This is expected AWS functionality, not an AWS vulnerability.

## Service model

- SageMaker `CreateJob`, `ListJobs`, `DescribeJob`, `StopJob`, and `DeleteJob` manage `AgentRFT` and `AgentRFTEvaluation` model-customization jobs. These are separate from legacy training jobs and are not returned by `ListTrainingJobs`.
- Job Runtime API version: `2026-02-01`; endpoint: `https://job-runtime.sagemaker.<region>.api.aws`; signing name and IAM namespace: `sagemaker`.
- Runtime operations:
  - `Sample` and `SampleWithResponseStream` route OpenAI-compatible inference requests to the policy model and append prompt/response turns to a trajectory;
  - `CompleteRollout` seals a trajectory as `ready` or `failed`;
  - `UpdateReward` supplies one numeric reward per turn and transitions a sealed trajectory to reward-received state.
- Job resource shape: `arn:aws:sagemaker:<region>:<account>:job/<type>/<name>`.
- Every operation receives a job ARN and trajectory ID. Completion and reward mutation require an existing active trajectory; inert unknown IDs returned not found.

## Bearer-token construction and authorization

The current official `sagemaker-core` 2.23.0 token generator was inspected from a temporary install. It performs no AWS API request. It creates a presigned SigV4 `POST` for `https://sagemaker.amazonaws.com/?Action=CallWithBearerToken`, appends `Version=1`, base64-encodes it, and prefixes `sagemaker-api-key-`. The default and maximum expiry are 12 hours.

The token contains a Region-specific SigV4 credential scope but no job ARN or trajectory ID. Those are supplied separately on each Runtime request. The current `sagemaker-train` client uses the token as `Authorization: Bearer ...` for sampling, completion, and reward paths.

Live least-privilege controls established that bearer authorization is conjunctive:

1. An assumed-role session with only exact-job `sagemaker:CompleteRollout` reached the SigV4 API and received `ResourceNotFoundException` for an inert trajectory. Its ungranted `UpdateReward` call was denied.
2. A session with only `sagemaker:CallWithBearerToken` was denied both a direct SigV4 `CompleteRollout` and a correctly formatted bearer `CompleteRollout`; the latter explicitly said the named `sagemaker:CompleteRollout` action was missing.
3. A session with `CallWithBearerToken` plus `CompleteRollout` on exact synthetic job A reached the bearer service and returned trajectory-not-found. The same token/request against synthetic job B was denied on B's job ARN.
4. A token signed for `eu-west-1` was rejected by the `us-east-1` endpoint. A one-second token was rejected after expiry. A foreign-account job ARN was denied.

Therefore `CallWithBearerToken` is an additional bearer-authentication gate, not a wildcard substitute for `Sample`, `CompleteRollout`, or `UpdateReward`. The named action retains exact job-resource enforcement. Token generation alone is invisible and succeeds locally even when the signer lacks either permission; the service enforces both when consuming a bearer request.

## Attack matrix

| Idea | Result / boundary | Disposition |
| --- | --- | --- |
| Prematurely seal another live trajectory | `CompleteRollout` is job-scoped and accepts a caller-supplied trajectory ID; a compromised agent receives the live job/trajectory metadata. | Published as training-integrity post-exploitation |
| Falsify rewards | `UpdateReward` accepts one caller-selected double per turn after completion. This directly controls labels used by RFT/evaluation. | Published as model/training-data poisoning |
| Append attacker turns | `Sample`/streaming capture attacker prompt and model response into the named trajectory. Requires a live model/job and correct metadata. | Included as an optional variant, not overclaimed as standalone model access |
| `CallWithBearerToken` bypasses named runtime actions | Rejected live: bearer calls still need the underlying exact-job action. | Secure boundary |
| Token bypasses job resource scoping | Rejected live: exact job A authorization did not work for B. | Secure boundary |
| Cross-account job access | Rejected live with a synthetic foreign-account ARN; AWS's managed policy also enforces same principal/resource account. | Secure boundary |
| Cross-Region token use | Rejected live. | Secure boundary |
| Expired token replay | Rejected live. Ordinary unchanged pre-expiry replay remains inherent to a bearer token and requires a live job to test end to end. | Expected credential property |
| Trajectory IDOR across two real jobs | No live job existed, so no valid trajectory pair was available. Exact job IAM scoping was enforced before lookup. | Retain for a future two-job fixture |
| NaN/Infinity or reward-cardinality parser abuse | No active trajectory; cannot safely distinguish parser validation from trajectory-state validation. | Retain for future fixture; do not publish |

## Inventory and availability

- `ListJobs --job-category AgentRFT` and `AgentRFTEvaluation` returned empty in `us-east-1`.
- `eu-west-1` returned `UnknownOperationException` for both categories and had no Job Runtime endpoint.
- Legacy `ListTrainingJobs` was also empty in both Regions, but it is not the authoritative inventory for this feature.
- The `us-east-1` Runtime endpoint was live. Inert calls used deliberately nonexistent job/trajectory identifiers and created or modified no trajectory.
- No paid model-customization job was launched: a meaningful end-to-end fixture requires model training, an agent runtime/Lambda forwarder, datasets, storage, and compute, so it was not justified merely to reconfirm the documented trajectory transitions.

## Telemetry

- `ListJobs` and `DescribeJob` are ordinary SageMaker management events.
- AWS documents `Sample`, `SampleWithResponseStream`, `CompleteRollout`, and `UpdateReward` as opt-in `AWS::SageMaker::Job` data events. They are absent from Event History and default trails; sample request parameters are omitted even when enabled.
- Token generation is local and creates no CloudTrail event. An accepted bearer request is authorized and attributed as its underlying Job Runtime operation.
- The account's only trail did not select SageMaker Job data events, so no logging fixture was retained or created for this audit.

## Cleanup

No SageMaker job, trajectory, agent, Lambda, AgentCore runtime, model, bucket, role, policy, trail, or log group was created. All restricted sessions were temporary STS sessions and expired naturally. Temporary SDK inspection directories remain under `/tmp` only for the active research process and contain no AWS credentials or generated bearer tokens.

During the telemetry preflight, a stale prior-research fixture was discovered: `ht-nova-audit-20260929` was still logging to dedicated bucket `ht-nova-ct-228478051196-20260929`. It was stopped and deleted, every generated object was removed, the dedicated bucket was deleted, and exact trail/bucket checks returned not found.
