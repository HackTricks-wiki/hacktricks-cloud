# Step Functions callback-token binding audit — 2026-09-26

## Scope and result

Two disposable, same-account test cycles exercised Activity callback tokens in account
`228478051196`, `us-east-1`. The callback principal was an assumed role with only:

```text
states:SendTaskHeartbeat
states:SendTaskSuccess
states:SendTaskFailure
```

Those actions do not support resource-level authorization, so their minimum usable IAM resource is
`*`. The test role had no Step Functions list, describe, start, stop, poll, or state-machine mutation
permission. Setup and Activity polling were performed separately by the authorized administrator;
tokens stayed in process memory and test output contained only SHA-256 prefixes.

No token crossed an execution or Region boundary, no closed token changed a terminal result, and no
security vulnerability was established. The two service quirks below are retained for future
regression testing, but neither currently has enough security impact for an AWS report.

## Binding and lifecycle matrix

| Test | Live result | Assessment |
| --- | --- | --- |
| Heartbeat on a live token | HTTP 200; execution remained `RUNNING` | Expected |
| Token A with output labelled for execution B | A became `SUCCEEDED` with that output; B remained `RUNNING` | Expected: the token is the sole task capability |
| Token A used against `eu-west-1` while its task was in `us-east-1` | `InvalidToken`; primary execution remained `RUNNING` | Secure |
| One-character mutation of a live token | `InternalFailure`; original execution remained `RUNNING` | Fail closed, but wrong error class; see quirk below |
| `SendTaskSuccess` or `SendTaskFailure` replay after success | `TaskTimedOut`; terminal output unchanged | Secure |
| Any callback action replay after failure | `TaskTimedOut`; terminal error/cause unchanged | Secure |
| Success with a token after the Activity state's absolute timeout | `TaskTimedOut`; execution was already `FAILED` with `States.Timeout` | Secure |

The failure path used only a benign marker. The state-machine execution role had no permission policy,
and the state machine contained one Activity task and no downstream AWS integration.

## Quirk 1: immediate post-success heartbeat race

In both cycles, the first `SendTaskHeartbeat` issued immediately after `SendTaskSuccess` and an observed
`SUCCEEDED` execution returned HTTP 200. `SendTaskSuccess` and `SendTaskFailure` replays already returned
`TaskTimedOut`. In the repeat cycle, heartbeat replay returned `TaskTimedOut` after two seconds and again
after another eight seconds.

The API reference says `TaskTimedOut` covers a token whose associated task is already closed, so the
immediate 200 is documentation-inconsistent eventual behavior. It did not revive the task, change the
completed output, extend the absolute timeout, or make a later terminal replay succeed. A token holder
can already distinguish malformed and formerly valid tokens with terminal callback errors. With no new
authorization bypass, integrity impact, secret disclosure, or availability effect, this is not being
reported as a vulnerability.

## Quirk 2: corrupted token returns `InternalFailure`

Changing one character in the middle of a live token produced `InternalFailure` twice rather than the
documented `InvalidToken`. Botocore's standard retry behavior retried the 5xx response, so CloudTrail
showed several `SendTaskHeartbeat` attempts. Every attempt failed closed and the original execution stayed
`RUNNING`; the unmodified token still worked afterward. This is a robustness/error-contract defect, not
a demonstrated security issue.

## Telemetry

- Callback calls were default CloudTrail management events with `managementEvent: true`,
  `eventCategory: Management`, and `readOnly: false`.
- `requestParameters` contained `taskToken`; success additionally had `output`, and failure had `error`
  and `cause`. Existing live research established that callback payloads are hidden while the opaque token
  is retained.
- The malformed-token retries appeared in Event History as `errorCode: UnknownError` and
  `errorMessage: An unknown error occurred`, even though botocore surfaced `InternalFailure`.
- `GetActivityTask` remains an opt-in `AWS::StepFunctions::Activity` data event and was intentionally not
  re-tested with a new trail in this cycle.

## Cleanup

Both cycles terminated every execution before deletion, then deleted the state machine, Activity, callback
role/inline policy, and empty execution role. Independent checks found no matching Activity or IAM role.
State-machine deletion is asynchronous: the API reported `DELETING` before the names disappeared from
listing. No logging, X-Ray, queue, Lambda, bucket, key, or CloudTrail resource was created.

## Follow-ups

- Re-test both quirks in another Region or with a `.waitForTaskToken` service integration only if a
  plausible security impact is identified; error-code differences alone do not justify more infrastructure.
- A true cross-account callback-token rejection test needs a second account that is explicitly authorized.
  Do not use the base-profile account merely because credentials exist there.
- Keep callback actions at `Resource: "*"` in minimum-permission examples, and scope
  `states:GetActivityTask` separately to exact Activity ARNs.
