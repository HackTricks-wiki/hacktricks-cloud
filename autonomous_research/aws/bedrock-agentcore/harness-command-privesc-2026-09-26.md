# AgentCore Harness `CreateHarness` + `InvokeAgentRuntimeCommand` — 2026-09-26

## Result

**Verified end to end** in account `228478051196`, `us-east-1` with disposable, isolated IAM users:

1. A caller with the AgentCore composite-create actions but without `iam:PassRole` received an explicit `AccessDeniedException` for `iam:PassRole` on the supplied execution role.
2. A caller with the same policy plus `iam:PassRole` scoped to the exact role created a harness that reached `READY`. `GetHarness.executionRoleArn` matched the role.
3. `InvokeAgentRuntimeCommand`, addressed through the full harness ARN, ran:

   ```text
   id -u; python -c "import boto3; print(boto3.client('sts').get_caller_identity()['Arn'])"
   ```

4. The stream returned exit code `0`, stdout UID `0`, and an assumed-role ARN for the exact execution role. This proves a root shell in the microVM and AWS API access as the passed role.

This is an expected AWS feature and a privilege-escalation technique, not an AWS vulnerability.

## Caller permissions

Working create-and-invoke action set:

- `bedrock-agentcore:CreateHarness`
- `bedrock-agentcore:CreateAgentRuntime`
- `bedrock-agentcore:CreateAgentRuntimeEndpoint`
- `bedrock-agentcore:GetAgentRuntime`
- `bedrock-agentcore:GetAgentRuntimeEndpoint`
- `bedrock-agentcore:CreateWorkloadIdentity`
- `bedrock-agentcore:GetWorkloadIdentity`
- `bedrock-agentcore:CreateMemory`
- `bedrock-agentcore:GetMemory`
- `bedrock-agentcore:InvokeAgentRuntimeCommand`
- `bedrock-agentcore:InvokeAgentRuntime`
- `iam:PassRole` on the exact target role

`bedrock-agentcore:TagResource` was also required when tags were supplied; the final minimal probe omitted tags. The account needed the `AWSServiceRoleForBedrockAgentCoreRuntimeIdentity` service-linked role. It was created before the probe and deleted afterward.

The dependency-discovery sequence produced explicit authorization failures for `CreateAgentRuntimeEndpoint`, `CreateWorkloadIdentity`, and `GetAgentRuntime`. The remaining actions above were part of the final working set but were not each removed in isolation, so do not overstate every item as independently minimal.

### PassRole condition follow-up

A probe using `iam:PassedToService = bedrock-agentcore.amazonaws.com` did not satisfy the composite `CreateHarness` PassRole check, while exact-role `iam:PassRole` without that condition did. This may reflect a different/missing service context on the new composite API. Retest the condition independently before publishing it as a platform quirk.

## Harness command addressing

The SDK field name is misleading for harness-managed runtimes:

| Value supplied to `agentRuntimeArn` | Other parameter | Result |
| --- | --- | --- |
| Generated managed **runtime ARN** | none | Rejected: runtime is managed by a harness and cannot be invoked directly |
| Generated runtime ARN | `accountId` | Rejected: ARN and account ID are an invalid combination |
| Short harness ID | `accountId` | Interpreted as a normal runtime ID; `ResourceNotFoundException` |
| Full **harness ARN** | none | Success; command returned UID 0 and the passed-role STS ARN |

The working boto3 call is therefore:

```python
client.invoke_agent_runtime_command(
    agentRuntimeArn=harness_arn,
    runtimeSessionId=session_id,
    body={"command": command, "timeout": 60},
)
```

## Logs and detection evidence

- Event History contained both successful and denied `CreateHarness` management events.
- `requestParameters` contained `harnessName` and the full `executionRoleArn`.
- The positive response contained the harness ARN/ID and passed role. `environmentVariables` and `systemPrompt` were redacted as `***`.
- `resources.type` was `AWS::BedrockAgentCore::Runtime`, with the harness resource ARN pattern.
- The denied event recorded `AccessDenied` and the exact missing `iam:PassRole` message.
- `InvokeAgentRuntimeCommand` is a CloudTrail data event and was absent from Event History because data-event collection was not enabled.
- The runtime tried to write telemetry to `/aws/bedrock-agentcore/runtimes/...`, but the deliberately empty execution role lacked `logs:PutLogEvents`. The command still completed successfully. No matching log group existed, so CloudWatch command-text visibility depends on granting/configuring runtime logging.

## Cleanup

Each attempt used unique names and a `finally` teardown. The final cleanup verifies:

- harness list: no matching harness
- negative and positive IAM users: `NoSuchEntity`
- execution role: `NoSuchEntity`
- service-linked-role deletion task: reached `SUCCEEDED` (the role remained briefly visible after the task was requested)

## Publication

Added the technique, impact, exact invocation form, logs table, stealth rating, enumeration commands, and AWS references to `aws-bedrock-agentcore-privesc/README.md`. Also added missing stealth ratings to the four pre-existing AgentCore techniques encountered during the review.
