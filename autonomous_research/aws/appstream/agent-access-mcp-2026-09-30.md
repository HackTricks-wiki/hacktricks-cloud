# AppStream AgentAccess MCP headless desktop control — 2026-09-30

## Outcome

Verified end to end that an exact-stack `appstream:UpdateStack` caller can enable WorkSpaces
Applications AgentAccess, including vision, computer input, MCP forwarding, and
`UserControlMode=DISABLED`. A separate least-privilege operator then used exact stack+fleet
`CreateStreamingURL` and stack-conditioned AgentAccess MCP permissions to initialize a session and
receive a desktop screenshot without Describe or PassRole permission.

Expected AWS functionality only. No AWS defect or private report.

## Authorization and security model

- Updating an ordinary stack required deleting `USER_SETTINGS` and
  `STREAMING_EXPERIENCE_SETTINGS` in the same request; leaving either incompatible default caused
  `InvalidParameterCombinationException`.
- `UpdateStack` succeeded with only the exact stack ARN. `DescribeStacks` and a session policy
  naming a different stack ARN were denied.
- `CreateStreamingURL` required the exact stack and fleet ARNs, as in the ordinary bearer-URL path.
- AgentAccess uses `Resource: "*"`; individual tool actions were constrained by the
  `agentaccess-mcp:StackArn` condition. The live operator had only `InvokeMcp`,
  `CheckConnectionStatus`, and `GetScreenshot`.
- The stack exposed all input tools because its configuration enabled computer input, but the live
  operator's IAM policy did not authorize those actions and no keyboard or mouse input was sent.
- `UserControlMode=DISABLED` means users cannot view or stop the agent session. This is documented
  functionality, not a bypass.

## End-to-end proof

Account `228478051196`, Region `us-east-1`. The fixture used a disposable On-Demand
`stream.standard.small` fleet, Desktop view, one desired instance, the current public
`AppStream-WinServer2022-08-31-2026` image, and a disposable stack.

The restricted updater enabled all three AgentAccess settings. After the fleet reached RUNNING,
the restricted operator minted a 300-second streaming URL without listing/describing either
resource. The URL value was never printed. A SigV4 MCP connection in polling mode initially
returned only `agentaccess___connection_status`, progressed from CONNECTING to CONNECTED, and then
listed the vision/input tools. `agentaccess___screenshot` returned one JPEG response with a base64
length of 43,816 characters. The image was not printed, decoded, or stored, and S3 screenshot
upload was disabled.

The machine-input actions are established by the service's returned tool list and AWS
documentation; they were deliberately not exercised. Conditional access to a fleet machine role
has the same shell/application prerequisites as the already verified ordinary streaming-URL
technique.

## Telemetry

- The default `UpdateStack` management event retained the exact deleted attributes, all agent
  action settings, `UserControlMode`, format, resolution, and upload flag in the request. The full
  resulting configuration appeared in the response.
- `CreateStreamingURL` retained stack/fleet/validity while replacing the user ID, session context,
  and returned URL with `HIDDEN_DUE_TO_SECURITY_REASONS`.
- AWS documents agent connection/tool/end events as CloudTrail data events that require explicit
  trail configuration. They are not default Event History management events.
- AgentAccess publishes CloudWatch invocation, latency, error, session-start, and duration metrics.
- Screenshot S3 objects exist only when upload is enabled and the connecting principal has
  `s3:PutObject`; the proof used the direct MCP response only.

## Negative branches and setup observations

- A zero-desired-capacity On-Demand fleet cannot be started; the API requires at least one.
- The account had no valid `AmazonAppStreamServiceAccess` role, so the proof created the documented
  `/service-role/AmazonAppStreamServiceAccess` role with the AWS-managed service-role policy. An
  earlier attempt stopped before fleet creation when that role was absent.
- The latest public Windows image supported AgentAccess. Elastic, multi-session, Linux, and VPC
  endpoint variants were excluded by documented service limitations rather than tested.

## Cleanup evidence

The MCP client sent DELETE with session expiry enabled, and the cleanup handler independently
expired the returned session ID. The fleet progressed through STOPPING to STOPPED, was
disassociated and deleted, and the stack was deleted. The temporary service role was detached and
deleted. Final independent inventories returned zero matching stacks, fleets, AppStream network
interfaces, `AmazonAppStreamServiceAccess` roles, and AppStream autoscaling roles. No S3 bucket,
object, application, app block, custom image, machine role, or persistent network resource was
created. Local test scripts and virtual environments were also removed.

## Primary sources

- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_UpdateStack.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/agent-access-setup.html
- https://docs.aws.amazon.com/appstream2/latest/developerguide/agent-access-mcp-server.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_agentaccess-mcp.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_appstream.html
- https://docs.aws.amazon.com/appstream2/latest/APIReference/API_CreateStreamingURL.html
- https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AmazonAppStreamServiceAccess.html
