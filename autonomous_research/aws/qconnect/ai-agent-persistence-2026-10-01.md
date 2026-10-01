# Amazon Q in Connect AI-agent default persistence — 2026-10-01

## Outcome

Documented expected service-level persistence through `wisdom:UpdateAssistantAIAgent`. A principal
can replace one assistant's default for an AI-agent use case with a published custom agent version.
The version is selected for future Connect Customer contacts and associated Q sessions until the
mapping changes, surviving revocation of the writer's IAM session.

This is expected AWS functionality. No authorization defect was found and no private vulnerability
report was created.

## Current model

- CLI namespace: `qconnect`; IAM prefix and ARN service: `wisdom`.
- `UpdateAssistantAIAgent` supports the required Assistant resource type:
  `arn:aws:wisdom:<region>:<account>:assistant/<assistant-id>`.
- The request maps one agent type to an AI-agent ID qualified as `<id>:<version>`.
- A published immutable prompt version can be referenced by an agent; a published immutable agent
  version can then be set as the assistant default.
- Session-level agent configuration overrides assistant configuration, which overrides AWS system
  defaults. The assistant mapping is therefore durable for new sessions but is not universal over
  sessions that carry their own override.
- The Service Authorization Reference lists no `iam:PassRole` dependency for prompt creation,
  prompt versioning, agent creation, agent versioning, or the default mapping. Association creation
  is a different workflow and can have PassRole dependencies.

Full malicious-chain permissions, when no suitable custom version already exists:

| Step | IAM scope |
| --- | --- |
| Create custom prompt | `wisdom:CreateAIPrompt` on `*` |
| Publish prompt version | `wisdom:CreateAIPromptVersion` on its AIPrompt ARN |
| Create custom agent referencing the prompt version | `wisdom:CreateAIAgent` on `*` |
| Publish agent version | `wisdom:CreateAIAgentVersion` on its AIAgent ARN |
| Set default | `wisdom:UpdateAssistantAIAgent` on the exact Assistant ARN |

If tags are supplied at creation/version time, tagging authorization may also apply. An existing
draft takeover substitutes exact-resource `UpdateAIPrompt` / `UpdateAIAgent` for the corresponding
creation actions. The final mapping action alone is useful only when a compatible published version
already exists and its ID is known.

## Safe live authorization proof

Authorized account `228478051196`, Region `us-east-1`.

`ListAssistants --max-results 100` returned zero assistants. No Q, Connect, KMS, IAM, logging, or
other persistent fixture was created.

Assumed `ChackBotAdministratorRole` with an inline STS session policy containing only
`wisdom:UpdateAssistantAIAgent` on:

```text
arn:aws:wisdom:us-east-1:228478051196:assistant/11111111-1111-4111-8111-111111111111
```

The request used a syntactically valid nonexistent assistant ID, `MANUAL_SEARCH`, and a nonexistent
version-qualified agent ID. Results:

| Probe | Result | Meaning |
| --- | --- | --- |
| Update allowed synthetic assistant | `ResourceNotFoundException: Assistant does not exist` | exact permission passed; referenced-agent validation was not reached |
| Update different synthetic assistant | IAM `AccessDeniedException` naming the different Assistant ARN | resource scoping enforced |
| `GetAssistant` on allowed assistant | IAM `AccessDeniedException` | metadata read is not inherited or required for the write |

The STS policy included no list/read, prompt/agent, Connect, Bedrock, KMS, logs, or `iam:PassRole`
action. It created no IAM resource and expires naturally.

## Telemetry

The documented event source is `qconnect.amazonaws.com`, matchable in EventBridge with
`source: aws.qconnect`. After propagation, Event History contained both failed
`UpdateAssistantAIAgent` calls as management writes with `readOnly:false`. The request retained the
complete assistant ID, `MANUAL_SEARCH` type, and version-qualified custom agent ID. The allowed call
had `ResourceNotFoundException`; the disallowed-resource call had `AccessDenied` and named the
evaluated Assistant ARN. The successful-write response was not tested, so the public technique also
directs defenders to reconcile the assistant mapping and version contents.

## Impact boundaries

The persisted version can change selected prompts, guardrail selection, knowledge-base search
configuration, locale, or orchestration/tool decisions supported by its agent type. It can corrupt
recommendations and responses, influence tool use, or expose information through the Q experience.
It does not create arbitrary AWS permissions: actual reach is bounded by configured tools,
associations, guardrails, and downstream authorization. It is assistant/use-case persistence, not
IAM or account persistence.

## Rejected or deferred ideas

- `UpdateSession` can set a higher-precedence version for one exact session, but this is a narrower
  session mutation rather than durable assistant-wide persistence and adds little beyond the public
  assistant-default technique.
- No end-to-end custom prompt or agent was created because the account had no assistant, and session
  lifecycle/retention makes a fully disposable fixture nontrivial. Official APIs and examples define
  the version/publishing behavior; live validation is limited to the exact final-action IAM boundary.
- Cross-assistant prompt/agent references, version-qualifier confusion, deleted-version execution,
  cross-account identifiers, unauthorized tool-resource references, and session override leakage are
  retained as future vulnerability hypotheses. They require a safely disposable populated assistant
  and must not be represented as working attacks without validation.

## Cleanup

Vacuous: no resource was created or mutated. Final `ListAssistants` inventory was empty. The only
ephemeral state was a 15-minute STS session.

## Primary sources

- https://docs.aws.amazon.com/service-authorization/latest/reference/list_q-in-connect.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_UpdateAssistantAIAgent.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_CreateAIPromptVersion.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_CreateAIAgentVersion.html
- https://docs.aws.amazon.com/connect/latest/APIReference/API_amazon-q-connect_UpdateSession.html
- https://docs.aws.amazon.com/connect/latest/adminguide/create-ai-agents.html
- https://docs.aws.amazon.com/connect/latest/adminguide/create-ai-prompts.html
- https://docs.aws.amazon.com/eventbridge/latest/ref/events-ref-qconnect.html
