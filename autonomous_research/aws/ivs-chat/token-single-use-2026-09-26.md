# IVS Chat token single-use boundaries — 2026-09-26

## Outcome

No AWS vulnerability found. IVS Chat enforced its documented one-token/one-connection rule across
sequential replay, mutation, Region confusion, an already-live duplicate, and five eight-way races.
The existing public `CreateChatToken` technique was retained and completed with verified minimum IAM,
impact, stealth, and logging coverage.

## Fixture and minimum permission

- One disposable room in `us-east-1`, with no logging configuration and no messages sent.
- Restricted role allowed only `ivschat:CreateChatToken` on the exact room ARN.
- Explicit `GetRoom`, `ListRooms`, `UpdateRoom`, and `DeleteRoom` denies.
- `ListRooms` and a token request for a one-character-different room ARN both returned
  `AccessDeniedException`; minting for the exact room succeeded.
- Tokens used synthetic user IDs and attributes and `SEND_MESSAGE`, with three-minute sessions.
- Evidence retained only SHA-256 token prefixes, lengths, expiration timestamps, HTTP status, and
  timing. Raw bearer tokens were never printed.

## Data-plane boundary matrix

| Case | Result |
| --- | --- |
| First valid use | HTTP 101 WebSocket connection |
| Same token after the first socket closed | HTTP 400 |
| One-character-mutated token | HTTP 400; untouched token then connected |
| Valid token at `eu-west-1` endpoint | HTTP 400; original `us-east-1` use then connected |
| Second use while first socket stayed connected | HTTP 400 |
| Eight-way race, round 1 | 1 HTTP 101, 7 HTTP 400 |
| Eight-way race, round 2 | 1 HTTP 101, 7 HTTP 400 |
| Eight-way race, round 3 | 1 HTTP 101, 7 HTTP 400 |
| Eight-way race, round 4 | 1 HTTP 101, 7 HTTP 400 |
| Eight-way race, round 5 | 1 HTTP 101, 7 HTTP 400 |

The failed mutation and wrong-Region attempts did not consume the valid token. No larger race was
warranted because every bounded repetition showed atomic single-use enforcement.

## Telemetry

- `CreateChatToken` is an IVS Chat control-plane API recorded by CloudTrail; Event History had not
  delivered the fixture events during the initial 15-second lookup, so do not infer a logging gap
  from immediate absence.
- WebSocket authentication and messaging are not signed IAM API calls. CloudWatch exposes aggregate
  connection and delivery metrics. Optional Chat Logging can retain room messages to CloudWatch Logs,
  S3, or Firehose.
- The test sent no message, so it incurred no IVS Chat message-send/delivery charge.

## Cleanup

The room was deleted and the restricted role/policy removed in `finally`. Independent `ListRooms` and
IAM inventory checks returned no matching resources.
