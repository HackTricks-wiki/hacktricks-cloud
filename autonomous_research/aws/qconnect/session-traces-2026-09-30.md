# Amazon Q in Connect session message/span reads — 2026-09-30

## Outcome

Verified the live authorization boundary and documented a new post-exploitation technique for:

- `wisdom:ListMessages` — session participant text, citations, guardrail state, and tool results
- `wisdom:ListSpans` — system instructions, LLM inputs/outputs, reasoning, tool invocations/results,
  prompt/model metadata, contact identifiers, guardrail assessments, and timing/token data
- `wisdom:SearchSessions` — exact-name session ID/ARN resolution under a known assistant

This is expected AWS functionality. No defect was found and no private vulnerability report was
created.

## Documentation model

The current CLI namespace is `qconnect`, while the IAM prefix and resource ARN service remain
`wisdom`.

The Service Authorization Reference assigns `ListMessages` and `ListSpans` to the required Session
resource type:

```text
arn:aws:wisdom:<region>:<account>:session/<assistant-id>/<session-id>
```

Both actions support `aws:ResourceTag/<key>`. `SearchSessions` has no supported resource type and
therefore requires `Resource: "*"`; its API currently accepts only an exact `NAME EQUALS` filter.

No `GetSession`, `ListAssistants`, or `SearchSessions` dependency is listed for the two exact-session
reads. The response schemas show that `ListMessages --filter ALL` includes text/tool-result variants,
while span message values can be text, tool invocation, tool result, or model reasoning.

## Safe live authorization proof

Authorized account: `228478051196`; Region: `us-east-1`.

Count-only `ListAssistants` returned zero in `us-east-1`. `us-west-2` and `eu-central-1` were denied
by the account SCP, and `eu-west-1` had no reachable service endpoint. No existing conversation or
customer data was accessed.

The final test assumed `ChackBotAdministratorRole` with an inline STS session policy containing only:

- `wisdom:ListMessages` and `wisdom:ListSpans` on one synthetic exact session ARN
- `wisdom:SearchSessions` on `Resource: "*"`

Results:

| Probe | Result | Meaning |
|---|---|---|
| `ListMessages` on allowed synthetic session ARN | `ResourceNotFoundException: Assistant does not exist` | exact permission passed |
| `ListSpans` on allowed synthetic session ARN | same resource-not-found result | exact permission passed |
| `ListMessages` on different session ARN | `AccessDeniedException`; no session policy allowed it | session resource scoping enforced |
| `SearchSessions` for an exact synthetic name | assistant resource-not-found | global action permission passed |
| `GetSession` on the allowed session ARN | `AccessDeniedException`; no session policy allowed it | metadata read is not inherited |

The STS session policy created no IAM resource and expired naturally. Two preliminary temporary-role
attempts were stopped before any Q API call (one local CLI configuration error, one bounded STS
propagation/assumption failure); their cleanup traps ran, and independent `GetRole` checks confirmed
`ht-qconnect-readprobe-260930` absent.

No assistant or session was created because the service exposes no session-deletion API and the user
requires complete fixture cleanup.

## Telemetry

AWS documents EventBridge delivery of Amazon Q in Connect CloudTrail events with:

- `source: aws.qconnect`
- `eventSource: qconnect.amazonaws.com`

Event History delivered all five failed probes after propagation. Each used `eventCategory:
Management`, `readOnly: true`, and `eventSource: qconnect.amazonaws.com`. The calls retained the
assistant/session IDs or the complete `NAME EQUALS` search filter, recorded the expected
`AccessDenied`/`ResourceNotFoundException`, and used `responseElements: null`.

No successful data-returning session existed, so successful response-body logging remains unclaimed.
AI-agent CloudWatch logging is separately configurable and can contain full prompts, conversation
history, tool calls/results, model completion, and agent configuration.

## Remaining validation

An end-to-end response and successful-call CloudTrail test requires a disposable assistant plus a
session. Do not create this fixture until there is an approved cleanup/retention strategy for sessions,
because the API currently has no `DeleteSession` operation.

## Primary sources

- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_ListMessages.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_ListSpans.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_SpanAttributes.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_SpanMessageValue.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_SearchSessions.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_q-in-connect.html
- https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-qconnect.html
- https://docs.aws.amazon.com/connect/latest/adminguide/viewing-logs-for-connect-ai-agents-self-service.html
