# AgentCore Code Interpreter CloudTrail audit — 2026-09-26

## Finding

The [AWS CloudTrail supported data-event resource catalog](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html) lists `AWS::BedrockAgentCore::CodeInterpreter` for Bedrock AgentCore Code Interpreter API activity. The [AgentCore Code Interpreter overview](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html) also advertises CloudTrail logging capabilities. The book previously asserted that `StartCodeInterpreterSession`, `InvokeCodeInterpreter`, and `StopCodeInterpreterSession` could produce no CloudTrail record. Its earlier live test checked default Event History, which never includes data events, and was against AWS's system interpreter `aws.codeinterpreter.v1`.

The exact per-API mapping and whether selecting the system interpreter resource yields a caller-account data event are **not confirmed** by this audit. The book now says the calls are absent by default, notes the documented data-event resource type, and leaves these details open. [AgentCore observability documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability-tool-metrics.html) separately documents optional spans and application logs, which are not CloudTrail.

## Candidate tests

| Candidate | Category | Status | Next check |
| --- | --- | --- | --- |
| Capture session start, invocation, and stop on a custom interpreter with `AWS::BedrockAgentCore::CodeInterpreter` selector | Expected | Untested here | Use isolated resource and trail, inspect delivered events, delete both |
| Capture those events on AWS-managed `aws.codeinterpreter.v1` | Expected or potential gap | Untested; system ARN belongs to AWS | Compare system and custom interpreter behavior under the same selector |
| Command payload leakage into CloudTrail | Potential unexpected | No evidence | Inspect data-event redaction only after authorized controlled test; report locally if sensitive payload leaks contrary to AWS contract |

No AWS resources were created or left running in this audit. No zero-day claim.
