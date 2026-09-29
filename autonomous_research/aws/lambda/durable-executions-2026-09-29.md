# Lambda durable executions — 2026-09-29 audit

## Scope and hypotheses

This test examined two expected offensive paths and two potential authorization defects:

1. whether `GetDurableExecutionHistory` returns security-sensitive execution data;
2. whether a known callback ID plus a send-callback grant can alter workflow output;
3. whether permission on durable execution B can complete a callback owned by execution A; and
4. whether a successfully consumed callback ID can be replayed.

The test used only account `228478051196` in `us-east-1`. Randomized resource names, execution ARNs, and callback IDs are intentionally omitted from this ledger.

## Fixture

- Disposable Python 3.14 Lambda durable function with a single callback wait and a final result that reflected the callback response.
- Disposable execution role with the documented checkpoint/state permissions required by the durable SDK plus basic log delivery.
- Two concurrent qualified `$LATEST` durable executions, A and B, each paused on its own callback.
- Disposable tester role whose only callback mutation permission was `lambda:SendDurableExecutionCallbackSuccess` on execution B's exact ARN.

An initial unqualified invocation was rejected with `InvalidParameterValueException`, confirming that a durable function must be invoked through a qualifier. That preliminary function and its roles were deleted before the final cycle.

## Results

| Check | Result | Security conclusion |
| --- | --- | --- |
| History with `includeExecutionData=true` | Returned callback events and callback IDs for both executions | History is a sensitive post-exploitation data source |
| B-scoped role sends A's callback ID | `AccessDeniedException` naming execution A's ARN | Callback authorization follows the owning execution, not merely the opaque ID |
| Execution A after denied send | Remained `RUNNING` | The unauthorized request did not consume or alter the callback |
| B-scoped role sends B's callback ID | Success; B reached `SUCCEEDED` with the supplied JSON result | Matching send permission plus a leaked live callback ID permits workflow-result injection |
| Replay of B's callback ID | `CallbackTimeoutException` stating the callback timed out or was already completed | Consumed callback IDs are not replayable |

The cross-execution and replay 0-day hypotheses are therefore falsified. The history-disclosure and callback-injection paths are expected AWS behavior and are suitable for defensive book coverage.

## Minimum permissions and boundaries

- History disclosure: `lambda:GetDurableExecutionHistory` on the exact durable-execution ARN; `lambda:GetDurableExecution` is optional for the summary and `lambda:ListDurableExecutionsByFunction` is optional for discovery.
- Result injection: one of `lambda:SendDurableExecutionCallbackSuccess` or `lambda:SendDurableExecutionCallbackFailure` on the exact execution that owns a known, pending callback ID.
- Customer-managed-key executions additionally require the durable execution operator to have `kms:Decrypt` through Lambda for reads with execution data and callback operations. The live test used Lambda's default encryption, so this dependency was confirmed from the service documentation.
- The send API does not enumerate callback IDs. Plausible sources are authorized history access, broker/database access, logs, support artifacts, and compromised integration configuration.
- The test did not find a way to use an execution-B grant against execution A or to reuse a completed callback.

## Telemetry

CloudTrail Event History contained `GetDurableExecution` and `GetDurableExecutionHistory` as read-only management events under `lambda.amazonaws.com`. It also contained the fixture lifecycle events, with the versioned names `CreateFunction20150331` and `DeleteFunction20150331`.

Neither `SendDurableExecutionCallbackSuccess` nor `StopDurableExecution` appeared in default Event History during the observation window. This establishes only the default-history behavior observed in this test. Defenders should evaluate Lambda data-event selectors and application-level callback auditing rather than interpreting the absence as a guarantee that these calls can never be recorded. Lambda invocation and durable checkpoint operations are data events and are not present in default Event History.

## Cleanup and residue

- Stopped the still-waiting execution A; execution B was already `SUCCEEDED`.
- Deleted the Lambda function, execution role, restricted tester role, and CloudWatch log group.
- Deleted the deployment archive and source fixture from the local temporary directory.
- Verified all customer-created resources and local fixtures were absent.
- Durable execution retention cannot be set below one day and there is no per-execution delete API. The two terminal AWS-managed execution records therefore remain only until service retention expires; they incur no running compute and retain no customer-manageable infrastructure.

Cost was negligible (two short function starts and control-plane calls). No 0-day report was created.

## Sources

- https://docs.aws.amazon.com/lambda/latest/dg/durable-security.html
- https://docs.aws.amazon.com/lambda/latest/dg/durable-invoking.html
- https://docs.aws.amazon.com/lambda/latest/api/API_GetDurableExecutionHistory.html
- https://docs.aws.amazon.com/lambda/latest/api/API_SendDurableExecutionCallbackSuccess.html
- https://docs.aws.amazon.com/durable-execution/sdk-reference/operations/callback/
- https://docs.aws.amazon.com/lambda/latest/dg/durable-encryption.html
