# Step Functions dynamic HTTP Task credential capture — 2026-09-26

## Result

Verified end to end in account `228478051196`, `us-east-1`: an existing Standard state machine
contained one HTTP Task with a fixed EventBridge Connection but took `ApiEndpoint` from execution input.
A restricted assumed role holding only `states:StartExecution` on that exact machine supplied an
account-owned Lambda Function URL. The workflow succeeded and the collector received the exact API-key
header stored in the connection.

The caller was explicitly denied `states:DescribeStateMachine` and held no EventBridge, Secrets Manager,
Lambda, logs, state-machine update, or `iam:PassRole` permission. Knowledge of the state-machine ARN and
input field was enough. This is expected functionality reached through a dangerous workflow/IAM design,
not an AWS vulnerability.

## Fixture and minimum permissions

- EventBridge Connection: random canary API key in header `X-HT-Probe`.
- State machine: `ApiEndpoint.$ = $.endpoint`, method `GET`, fixed `InvocationConfig.ConnectionArn`.
- Execution role:
  - `states:InvokeHTTPEndpoint` on the exact state-machine ARN;
  - `events:RetrieveConnectionCredentials` on the exact connection ARN;
  - `secretsmanager:GetSecretValue` and `secretsmanager:DescribeSecret` on the connection's exact
    `events!connection/...` managed secret.
- Restricted caller: `states:StartExecution` on the exact state-machine ARN only.
- Collector: public Function URL in the same authorized account; its Lambda logged only the test header.

The technique also worked while `states:InvokeHTTPEndpoint` used `Resource: "*"`; the exact state-machine
scope is sufficient and preferable. The first two executions were started about five seconds after the
execution-role policy write and failed with `States.Http.AccessDenied`. Waiting twenty seconds for IAM
propagation made both wildcard and exact-resource variants succeed. This was propagation behavior, not an
additional permission gate.

## Security interpretation

The connection—not the `StartExecution` caller—holds the reusable API key, Basic credential, OAuth token,
and optional invocation headers/query/body. The state-machine role retrieves it and Step Functions merges
it into the outgoing request. Therefore a dynamic hostname plus a broad or absent `states:HTTPEndpoint`
condition turns a normal workflow invoker into a credential-exfiltration principal.

Defenses:

- keep the scheme and hostname static in ASL; parameterize only validated identifiers or a constrained path;
- restrict `states:InvokeHTTPEndpoint` with exact `states:HTTPEndpoint` and `states:HTTPMethod` conditions;
- use a different narrowly scoped connection per remote service/workflow;
- treat `states:StartExecution` as high impact whenever input reaches an HTTP endpoint, role ARN, resource
  identifier, command, deserializer, destination, or other sensitive sink.

## CloudTrail

- `StartExecution` was a default management event under the restricted caller. It named the state machine
  and execution, but `input` was `HIDDEN_DUE_TO_SECURITY_REASONS`, so the collector URL was absent.
- A default management `GetSecretValue` event appeared under the state-machine execution role with
  `invokedBy: states.amazonaws.com`. It named the exact `events!connection/...` secret and version, but not
  its value or the remote endpoint.
- `InvokeHTTPEndpoint` is an opt-in `AWS::StepFunctions::StateMachine` data event and was absent from Event
  History because no test trail/data selector was created.
- The successful Function URL call was visible in the disposable function's CloudWatch log. That endpoint
  logging is controlled by the remote service and is not reconstructable from the default Step Functions
  control-plane events.

## Cleanup

Five cycles were cleaned: two early fail-closed policy-propagation checks, one Lambda trust-propagation
failure, and two successful exact/wildcard role-scope checks. Final independent inventory checks showed
zero matching state machines, EventBridge Connections, generated connection secrets, Lambda
functions/URLs, CloudWatch log groups, or IAM roles.
No CloudTrail resource, bucket, API Gateway, VPC, KMS key, or external endpoint was created.

## Follow-ups

- `states:TestState` plus `iam:PassRole` can build an arbitrary one-state HTTP oracle without
  `states:RevealSecrets`; this is a distinct extension of the already documented TestState privesc and
  should be validated separately.
- Test whether an allowed endpoint can redirect to a disallowed hostname while retaining connection
  credentials. A cross-host redirect must be rejected, stripped, or re-authorized against the execution
  role's endpoint condition; successful forwarding would be reportable.
- Test OAuth `UpdateConnection` with only a changed authorization endpoint and omitted client parameters.
  Reuse of the stored client ID/secret against the replacement endpoint would be a separate credential-
  disclosure path.
