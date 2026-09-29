# Live Stream API — tested research

## 2026-09-28 — post-exploitation documentation and schema audit

No input, channel, asset, event, distribution, stream, bucket, IAM policy, or other cloud resource was created or changed. Current Google Cloud REST schemas, role/access-control docs, audit catalog, channel-activity logging docs, and product guides were reviewed. The installed gcloud version has no `gcloud livestream` command group, so examples use the documented REST interface.

### Retained book techniques

- A Live Stream Viewer can recover an RTMP distribution URI and plaintext `streamKey` from a channel resource (`livestream.channels.get`, with `.list` for discovery).
- A Viewer can recover an input's output-only RTMP/SRT ingest URI and inject compatible content when the endpoint is idle and its IP allowlist admits the attacker (`livestream.inputs.get`/`.list`).
- `livestream.assets.create` plus slate-event control can make the Live Stream service agent read a known supported media object and publish a transformed copy through an attacker-readable channel output.

### Material corrections

- Removed the claim that `channels.create` by itself exfiltrates victim data. A channel writes the stream sent to its input; an external output bucket alone does not read an existing victim object.
- Replaced the standalone `assets.create` disclosure claim with the complete asset-processing plus slate/output chain. Asset creation alone does not return the source bytes to the caller.
- Added the documented `securityRules.ipRanges` and duplicate-stream constraints to ingest hijack.
- Added the overlooked RTMP distribution stream-key disclosure visible in the documented channel response and REST schema.
- Corrected telemetry to exact catalog entries: get/list methods are off-default `ADMIN_READ` Data Access; create/start/event mutations are `ADMIN_WRITE` Admin Activity. Input connection events are product platform logs, but `channel_activities` logging is disabled by default.
- Used the documented per-bucket `roles/storage.objectAdmin` service-agent grant for an external channel sink rather than asserting an unvalidated object-creator-only configuration.

### Removed or folded

- Removed generic in-project service-agent GCS writes and external-bucket output as standalone H3s; without a victim data source or downstream consumer they are not independently consequential.
- Removed channel/input/event/asset deletion and stop actions as destructive-only denial of service.
- Folded external-bucket output into the supported-media slate chain as one possible attacker-readable destination.

### Official evidence used

- https://docs.cloud.google.com/livestream/docs/access-control
- https://docs.cloud.google.com/iam/docs/roles-permissions/livestream
- https://docs.cloud.google.com/livestream/docs/reference/rest/v1/projects.locations.channels
- https://docs.cloud.google.com/livestream/docs/reference/rest/v1/projects.locations.inputs
- https://docs.cloud.google.com/livestream/docs/how-to/distribute-live-streams
- https://docs.cloud.google.com/livestream/docs/how-to/insert-slate
- https://docs.cloud.google.com/livestream/docs/how-to/audit-logging
- https://docs.cloud.google.com/livestream/docs/how-to/logging

## 2026-09-28 — reciprocal cross-review

No cloud resource was read or mutated. A separate documentation pass checked the current REST schemas, access-control table, audit catalog, private-pool guide, and shell feasibility.

- Fixed the slate chain so it captures and polls the asset-creation LRO before creating the event; `livestream.operations.get` is therefore required, rather than optional, for the shown flow.
- Made the output boundary explicit: granting the service agent bucket access does not change a channel's `output`; the retained chain requires a running channel already configured to write to an attacker-readable destination.
- Added the missing network-reachability/private-pool prerequisite to ingest injection and provider-side acceptance controls to direct RTMP-key reuse.
- Revalidated `GetChannel`/`GetInput`/`GetOperation` as off-default `ADMIN_READ` Data Access and `CreateAsset`/`CreateEvent` as always-on `ADMIN_WRITE` Admin Activity. The documented REST payloads and resource paths match the examples.
