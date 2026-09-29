# Amazon Connect CreateParticipant audit — 2026-09-29

## Hypothesis and disposition

`connect:CreateParticipant` can mint a new live-interaction bearer without a Connect user session. This is expected functionality with a high-impact authorization consequence, not a service defect. Public post-exploitation coverage was added; no private report was created.

## Current API behavior and prerequisites

- Chat accepts only `ParticipantRole=CUSTOM_BOT`; the returned participant token must be exchanged through `CreateParticipantConnection` within 15 seconds.
- WebRTC voice accepts `ParticipantRole=CUSTOMER`; the original caller must be connected to an agent and enhanced multi-party contact monitoring must be enabled.
- `CreateParticipantConnection` accepts the bearer without SigV4 and can return chat websocket / connection credentials or WebRTC Chime meeting and attendee material.
- The Service Authorization Reference lists both Contact and Instance as required resource types for `connect:CreateParticipant`, with `connect:InstanceId` available as a condition key.

## Authorization probe

No Connect instances existed in `us-east-1`, so no paid instance or contact was created. A disposable IAM caller scoped to a synthetic exact Contact ARN reached service-side `ResourceNotFoundException`; the same was true when the corresponding synthetic Instance ARN was added. This verifies that IAM did not require broad `Resource: *`, but nonexistent resources cannot prove whether a real contact evaluates one or both ARNs. The public page therefore follows the stricter current AWS authorization table and names both.

## Telemetry

`CreateParticipant` is a Connect management write. The resulting Participant Service exchange and chat/WebRTC use are bearer-authenticated application data-plane operations rather than SigV4 calls by the original IAM principal. Defenders need contact participant/transcript, application and network telemetry in addition to CloudTrail.

## Cleanup

Both disposable access keys, inline policies and IAM users were deleted. Prefix-filtered inventory returned empty. No Connect instance, contact, participant or media session was created.
