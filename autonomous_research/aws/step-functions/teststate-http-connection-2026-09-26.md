# Step Functions TestState HTTP Connection oracle — 2026-09-26

## Result

Verified end to end in account `228478051196`, `us-east-1`: `states:TestState` plus exact-role
`iam:PassRole` executed a caller-supplied HTTP Task with `revealSecrets=false`. An account-owned HTTPS
collector received the exact canary API-key header stored in a fixed EventBridge Connection.

This is expected functionality and a concrete HTTP/credential-disclosure variant of the existing
TestState+PassRole privilege-escalation primitive. It does not require a state machine, an API Destination,
`states:RevealSecrets`, or direct permission to read the Connection or its Secrets Manager secret.

## Two-sided authorization proof

The first temporary principal held only `states:TestState` on `*`. Calling TestState with the execution
role was denied with `AccessDeniedException` naming the missing `iam:PassRole` permission.

The role's policy was then extended with only:

```json
{
  "Effect": "Allow",
  "Action": "iam:PassRole",
  "Resource": "arn:aws:iam::228478051196:role/<exact-test-role>",
  "Condition": {
    "StringEquals": {
      "iam:PassedToService": "states.amazonaws.com"
    }
  }
}
```

A fresh session succeeded. It held no EventBridge, Secrets Manager, Lambda, logs, state-machine CRUD,
or `states:RevealSecrets` permission.

The passed role trusted `states.amazonaws.com` with `aws:SourceAccount` pinned and held:

- `states:InvokeHTTPEndpoint` on `*`, conditioned to the exact collector URL and method `GET`;
- `events:RetrieveConnectionCredentials` on the exact Connection ARN;
- `secretsmanager:GetSecretValue` and `secretsmanager:DescribeSecret` on the exact generated secret.

TestState's `states:InvokeHTTPEndpoint` statement uses `Resource: "*"` because there is no state-machine
resource for an isolated tested state. Endpoint and method condition keys provide the meaningful scope.

## Why `revealSecrets=false` does not stop it

`states:RevealSecrets` governs redaction in TestState's inspection result. The remote HTTPS service must
still receive Connection credentials for the HTTP request to authenticate. A controlled endpoint sees
them directly, and a legitimate endpoint can be used as an authenticated read/write oracle whose response
is returned by TestState. The live test used `inspectionLevel=INFO`, explicitly set `revealSecrets=false`,
returned `SUCCEEDED`, and produced the canary header in the collector log.

## Telemetry

- `TestState` is a default management event. The role ARN is useful detection context, but the submitted
  state definition/input are redacted.
- The connection-secret read is a default Secrets Manager `GetSecretValue` management event attributed to
  the passed role with `invokedBy: states.amazonaws.com`; it names the secret but never its value.
- `InvokeHTTPEndpoint` is an opt-in `AWS::StepFunctions::StateMachine` data event. It is absent from Event
  History unless explicitly selected.
- The request and response bodies, Connection-injected credential, and remote-side observation are not
  reconstructable from the default management events.

## Cleanup

The combined validation also repeated the previously verified StartExecution path. The state machine,
EventBridge Connection and generated secret, Function URL/function, CloudWatch log group, execution/test/
caller/Lambda roles, inline policies, and all executions were removed. Independent inventory checks found
no matching residue after asynchronous state-machine deletion completed.

## Next defects to probe

- Endpoint allowlist redirect: allow only endpoint A in `states:HTTPEndpoint`; make A return a cross-host
  302/307 to B. B must not receive Connection authorization.
- OAuth partial update: change only a Connection's authorization endpoint while omitting client parameters.
  The old client ID/secret must not be sent to the replacement endpoint.
