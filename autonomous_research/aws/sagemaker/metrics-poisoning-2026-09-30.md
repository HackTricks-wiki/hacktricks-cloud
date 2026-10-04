# SageMaker Metrics Service poisoning audit — 2026-09-30

## Result

Verified that exact-resource `sagemaker:BatchPutMetrics` alone can append forged metrics to a completed experiment trial component. Duplicate coordinates coexist and alter aggregates; a new higher step becomes the later series point. Published this as experiment/model-selection integrity post-exploitation, bounded away from claims that it modifies a trained model or SageMaker Hyperparameter Tuning's internal objective result.

## API and IAM model

- Service/API: `sagemaker-metrics` / `2022-09-30`; endpoint prefix `metrics.sagemaker`; signing name/IAM namespace `sagemaker`.
- `BatchPutMetrics` accepts a lower-case trial-component name and up to ten points per request. Each point carries an arbitrary metric name, timestamp, optional non-negative step and double value.
- `BatchGetMetrics` accepts up to 100 queries against SageMaker resource ARNs. Each query chooses metric name, `Min`/`Max`/`Avg`/`Count`/`StdDev`/`Last`, period, x-axis type and optional bounds.
- Both actions support resource policies on `experiment-trial-component/<name>` and `training-job/<name>`, including normal resource-tag conditions.
- There is no metric-name condition key and no separate per-series resource. Exact component/job scoping is the finest native boundary.

## Live exact-action test

Created two zero-compute, metadata-only trial components in `us-east-1`:

- `ht-metrics-a-20260930`
- `ht-metrics-b-20260930`

Both were created directly in `Completed` state and tagged as HackTricks test fixtures. No experiment/trial association, training job, model, endpoint, S3 object or execution role was involved.

1. Admin wrote baseline `validation:accuracy`, step 1, value `0.9` to A.
2. A source-profile-assumed `ChackBotAdministratorRole` session was restricted to only `sagemaker:BatchPutMetrics` on A's exact `experiment-trial-component` ARN.
3. That session successfully submitted two points with `Errors: []`:
   - the same name/timestamp/step 1 with value `0.1`;
   - the same name/timestamp at step 2 with value `0.05`.
4. The same session was denied a write to B, and the denial named B's exact ARN.
5. `DescribeTrialComponent` on A was denied, confirming the writer had no ordinary component read/update authorization.
6. Admin `BatchGetMetrics` readback returned:
   - `Last`: x `[1,2]`, values `[0.9,0.05]`;
   - `Avg`: x `[1,2]`, values `[0.5,0.05]`;
   - `Count`: x `[1,2]`, values `[2.0,1.0]`.

The duplicate was therefore retained rather than overwriting the baseline. It changed aggregates/counts at step 1. The higher step became the later/latest series value. Metrics were accepted after the trial component was already `Completed`.

## Security boundaries and rejected overclaims

| Question | Result |
| --- | --- |
| Does `BatchPutMetrics` require component read/update? | No; exact write-only session succeeded while Describe was denied |
| Does exact component A authorize B? | No; B was denied on its exact ARN |
| Does a duplicate silently replace the original point? | No; both values remained and affected `Avg`/`Count` |
| Can an attacker append an apparently later result? | Yes; a new higher step was returned as the later point |
| Does `Completed` freeze metrics? | No; all writes were accepted after completion |
| Does this mutate a model/artifact/training container? | No |
| Does it necessarily change HPO's internal winner? | Not established and not claimed; HPO derives objectives through its training/tuning workflow |
| Can it affect human or custom automated selection? | Yes when Studio/`BatchGetMetrics` values are trusted |
| Cross-account access? | No Metrics Service resource-policy mechanism was found; normal IAM account/resource scope applies |

## Telemetry

- `BatchPutMetrics` and `BatchGetMetrics` did not appear in Event History.
- AWS documents Metrics Service activity as optional CloudTrail data events on `AWS::SageMaker::ExperimentTrialComponent`, selectable with advanced event selectors.
- When delivered via CloudTrail/EventBridge, the service source is `metrics-sagemaker.amazonaws.com` / `aws.metrics-sagemaker`.
- `CreateTrialComponent` and `DeleteTrialComponent` were default `sagemaker.amazonaws.com` management writes. Deletion events recorded the component names and returned ARNs.

High-value detections include unexpected writer roles, writes after component completion, far-forward step values, timestamps outside the run window, duplicate counts and series values inconsistent with immutable training logs.

## Cleanup

Both delete requests succeeded. Component B reached exact `ResourceNotFound` immediately. Component A entered the asynchronous `Deleting` state while SageMaker removed its metrics, then reached exact `ResourceNotFound`. A final filtered trial-component inventory was empty. No billable compute or supporting resource exists.
