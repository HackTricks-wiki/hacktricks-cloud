# Bedrock Agents Runtime CloudTrail audit — 2026-09-26

## Finding

The [current AWS Bedrock CloudTrail guide](https://docs.aws.amazon.com/bedrock/latest/userguide/logging-using-cloudtrail.html) says Agents Runtime API operations are **opt-in data events**. It explicitly names `InvokeAgent` with the advanced selector `resources.type = AWS::Bedrock::AgentAlias`, and `InvokeInlineAgent` with `AWS::Bedrock::InlineAgent`. `Retrieve` and `RetrieveAndGenerate` use `AWS::Bedrock::KnowledgeBase`. Runtime model calls such as `InvokeModel` and `Converse` are management events. No prompt or completion content is established by these CloudTrail event categories; model invocation logging and agent trace are separate.

Earlier live tests did not find `InvokeAgent`, `GetAgentMemory`, or `DeleteAgentMemory` in default Event History, while same-window management events appeared. This establishes default visibility, not that no data-event trail can record them. The guide says *all* Agents Runtime APIs are data events but does not explicitly name a selector for the two memory APIs. Keep that selector mapping as an open verification question.

## Book corrections

- Replaced absolute no-record claims for `InvokeAgent` in the privilege escalation and post exploitation pages.
- Marked the two memory APIs as data events per AWS's broad statement while flagging their selector mapping as unconfirmed.
- Added Bedrock enumeration CloudTrail guidance and stealth ratings to the affected techniques.

## Candidates

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| Invoke an agent after hijacking its action-group Lambda | Expected | Previously live verified; book covers | Inspect opt-in alias data record fields in an isolated test |
| Get/Delete agent memory with a correctly configured data-event selector | Expected logging behavior | Exact selector unverified | Find official event example or perform a scoped test, then update table |
| Alias data-event selector fails to record `InvokeAgent` | Potential unexpected | No evidence; do not report | Test only with a valid trail and controlled agent, then remove all resources |

No AWS resources were created or left running in this audit. No zero-day claim.
