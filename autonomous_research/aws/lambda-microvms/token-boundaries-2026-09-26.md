# Lambda MicroVM token authorization boundaries — 2026-09-26

## Result

Two expected attack paths were verified end to end against disposable Lambda MicroVMs in `us-east-1`:

1. `lambda:CreateMicrovmShellAuthToken` scoped to one exact MicroVM image ARN was sufficient to mint a shell token and execute commands as `uid=0(root)` inside a running MicroVM created from that image. The caller did not need discovery, lifecycle, application-token, S3, or PassRole permissions.
2. `lambda:CreateMicrovmAuthToken` scoped to one exact image ARN was sufficient to mint endpoint credentials for a running MicroVM created from that image. Port constraints were enforced, and `allPorts` authorized the listener as documented.

These are expected AWS features with high offensive impact, not AWS vulnerabilities. They were missing from the public book because Lambda MicroVMs launched in 2026.

## Fixture

Every attempt used a fresh `ht-microvm-<random>` prefix and:

- Lambda-managed base image `arn:aws:lambda:us-east-1:aws:microvm-image:al2023-1`;
- a 512 MiB / 0.25-vCPU image, the smallest supported size;
- a minimal Node HTTP application on port 8080;
- a ten-minute `maximumDurationInSeconds` hard stop;
- a build role limited to the one S3 artifact plus optional log writes;
- an execution role limited to one random S3 canary object;
- an attacker role with one exact-image token action plus explicit negative-control denies.

The image build and runtime logging configurations were disabled to keep the fixture small. Each MicroVM was terminated immediately after its matrix rather than relying on the hard stop.

## Shell-token proof

Final successful shell fixture:

- Prefix: `ht-microvm-5f8c761b04`
- Image: `arn:aws:lambda:us-east-1:228478051196:microvm-image:ht-microvm-5f8c761b04`
- MicroVM: `microvm-97ac9580-814d-390b-966f-7415dede426f`
- `CreateMicrovmShellAuthToken` request ID: `c0c9cd5c-f4e9-45a5-aec2-7f48237a6a21`
- Token length: 767 bytes; only its SHA-256 was retained.

The attacker allow was only:

```json
{
  "Effect": "Allow",
  "Action": "lambda:CreateMicrovmShellAuthToken",
  "Resource": "arn:aws:lambda:us-east-1:228478051196:microvm-image:ht-microvm-5f8c761b04"
}
```

Explicit denies covered `lambda:GetMicrovm`, `lambda:ListMicrovms`, `lambda:RunMicrovm`, `lambda:TerminateMicrovm`, `lambda:CreateMicrovmAuthToken`, `iam:PassRole`, `s3:GetObject`, and `s3:ListBucket`. All exercised negative controls returned explicit-deny errors before the successful shell call.

The target was launched with the AWS-managed `SHELL_INGRESS` connector. A WebSocket to the runtime endpoint offered the `lambda-microvms` and `lambda-microvms.authentication.<token>` subprotocols. The server returned a `session_init` text frame; binary PTY input using carriage return executed:

```text
uid=0(root) gid=0(root)
/
```

For the managed AL2023 image used here, the shell already landed inside the application container and `ctr` was absent. This differs from the current troubleshooting example, which describes a further `ctr task exec` step. The public technique therefore describes both observed/direct and documented/containerd paths.

AWS documentation states that an attached MicroVM execution role supplies short-lived credentials through IMDSv2. A live Node `fetch` attempt to the conventional metadata path returned a generic `TypeError`, so this run did **not** independently prove credential retrieval or canary access. The book treats role takeover as conditional on the documented execution-role delivery and does not claim the canary was read.

The service rejected a 61-minute shell token with `ValidationException: ExpirationMinutes 61 exceeded max allowed of 60.` This establishes the actual 1–60-minute bound even though the current API shape documents only a minimum.

## Application-token proof

Successful application fixture:

- Prefix: `ht-microvm-2861205e8e`
- Image: `arn:aws:lambda:us-east-1:228478051196:microvm-image:ht-microvm-2861205e8e`
- MicroVM: `microvm-ddff385a-640d-30f5-805e-4f4b5a12d239`
- Exact-port token request ID: `a86cb2c5-04de-470c-9bb0-f802840961d7`
- 9090-only token request ID: `e4485531-71f6-4712-afcc-31f8e4a2ea76`
- All-ports token request ID: `f1da9066-a439-40a9-8d3a-a44e8fffa0f5`

The runtime used the AWS-managed `ALL_INGRESS` connector. The attacker allow was only `lambda:CreateMicrovmAuthToken` on the exact image ARN; explicit denies covered the shell-token action, discovery, lifecycle, PassRole, and direct S3.

| Request | Result |
| --- | --- |
| Endpoint without `X-aws-proxy-auth` | HTTP 403 |
| Token limited to port 8080, request routed to 8080 | HTTP 200 and exact expected JSON |
| Token limited to port 9090, request routed to 8080 | HTTP 403 |
| Token with `allPorts`, request routed to 8080 | HTTP 200 and exact expected JSON |

Only response hashes and boolean fixture checks were retained. No token value or canary value was stored.

## Protocol lessons from failed iterations

The first two shell connections authenticated successfully but did not execute commands:

1. Sending the command in a WebSocket text frame caused it to be treated as terminal input text.
2. Sending binary input ending in line feed caused the PTY to echo but not submit the command.
3. The correct observed framing was one server `session_init` text frame, then binary terminal bytes with carriage return for Enter. Completion detection must ignore the echoed command.

These were client-fixture errors, not service-security outcomes. Each iteration still terminated and removed all AWS assets before the next build.

## Authorization and detection conclusions

- Both token APIs authorize against the backing image ARN even though their request contains only a runtime MicroVM ID. One image grant consequently covers every current and future runtime from that image.
- Neither token API required `iam:PassRole`, a runtime lifecycle action, or a discovery action when the ID and endpoint were known.
- `CreateMicrovmShellAuthToken`, `CreateMicrovmAuthToken`, `RunMicrovm`, and `TerminateMicrovm` are Lambda MicroVM data events. They are not logged by CloudTrail by default.
- `ListMicrovms` and `GetMicrovm` are default management events. Known identifiers avoid those events.
- Endpoint HTTP and PTY WebSocket traffic is not a CloudTrail API event. Downstream AWS calls remain attributable to the execution role.

Stealth rating for both known-identifier token paths: **High**.

## Cleanup verification

Every attempt performed the following in `finally`:

1. Terminate the MicroVM and wait for `TERMINATED`.
2. Delete the MicroVM image and wait until it is absent.
3. Delete every S3 object version/delete marker and the test bucket.
4. Delete inline policies and all three test roles.
5. Independently list images, non-terminated MicroVMs, buckets, and roles matching the unique prefix.

The final inventory after every run returned empty arrays for test images, live MicroVMs, buckets, and roles. Historical `TERMINATED` runtime records remain visible in `ListMicrovms`; they are terminal records, not running infrastructure.

## References

- https://docs.aws.amazon.com/lambda/latest/microvm-api/API_CreateMicrovmShellAuthToken.html
- https://docs.aws.amazon.com/lambda/latest/microvm-api/API_CreateMicrovmAuthToken.html
- https://docs.aws.amazon.com/service-authorization/latest/reference/list_lambda.html
- https://docs.aws.amazon.com/lambda/latest/dg/microvms-troubleshooting.html
- https://docs.aws.amazon.com/lambda/latest/dg/microvms-launching.html
- https://docs.aws.amazon.com/lambda/latest/dg/microvms-networking.html
- https://docs.aws.amazon.com/lambda/latest/dg/microvms-monitoring.html
- https://docs.aws.amazon.com/lambda/latest/dg/microvms-integrations-claude-managed-agents.html
