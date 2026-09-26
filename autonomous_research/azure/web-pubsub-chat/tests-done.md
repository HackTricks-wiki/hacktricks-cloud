# Web PubSub Chat — Tests Done

| # | Hypothesis | Minimum permission tested | Status |
|---|------------|---------------------------|--------|
| 1 | `chat/room/read` is isolated to the assigned hub child scope | Exact room read at `WebPubSub/hubs/chata` | **REFUTED 2026-09-26** — hub-child assignment produced no positive control; use the parent Web PubSub resource scope |
| 2 | `chat/room/read` cannot modify a room | Exact room read at parent Web PubSub resource | **PASS 2026-09-26** — both GETs 200; PUT 403 requiring `chat/room/write` |
| 3 | A listed Web PubSub key administers preview Chat data | `Microsoft.SignalRService/WebPubSub/listkeys/action` | **PASS 2026-09-26** — key JWT created a custom role and assigned it to a room member |

**Lab setup (2026-09-26):** Created a disposable Free_F1 Web PubSub service with Chat hubs `chata`
and `chatb`. Chat requires a system-assigned identity, a storage account with Storage Table Data
Contributor, and a `WebPubSub/persistentStorages` child resource. The hub's
`properties.chat.persistentStorage.id` must reference that child, not the storage-account ARM ID.
The stable Chat data-plane route tested was API `2026-02-01-preview`.

Seeded `room-a` in `chata` and `room-b` in `chatb` with a service-key JWT. A UAMI received a custom
role containing only `Microsoft.SignalRService/WebPubSub/chat/room/read`, first at the `chata` child
scope and later also at the parent Web PubSub resource for a propagation/scope control. The ACI probe
uses a fresh Entra token for audience `https://webpubsub.azure.com/`.

Authorization results:

- With only the `chata` child assignment, same-hub and sibling-hub GET both returned 403 after role
  propagation; this scope is not a usable positive control.
- Adding the same exact role at the parent resource made `chatb` readable. The duplicate child plus
  parent assignments temporarily coincided with `chata` returning 403; after the child duplicate was
  deleted and propagation continued, both hubs returned 200 under the parent assignment. The test
  cannot attribute that transient result to the duplicate assignment rather than cache/propagation.
  It granted no extra access and is not a security report.
- Under the working parent exact-read assignment, same-hub and sibling-hub GET returned 200 and the
  same-hub PUT returned 403 requiring `Microsoft.SignalRService/WebPubSub/chat/room/write`.
- A correctly assigned built-in Web PubSub Service Owner also returned 200 after propagation. An
  earlier service-principal control used its application ID rather than object ID and was discarded.

Service-key results:

- A JWT signed with the UTF-8 bytes of the literal `primaryKey` string and exact full-URL audience created
  `room.htrc-admin` with history, moderation, and publish permissions (HTTP 201).
- A second key-signed JWT assigned that role to a canary room member (HTTP 201).
- This confirms that `listkeys/action` extends to persistent Chat administration; Base64-decoding the
  returned key before HMAC signing is incorrect.

Logging observation: the parent advertises `HttpRequestLogs`, `MessagingLogs`, and
`ConnectivityLogs` diagnostic categories, all disabled in the disposable service. Chat calls are
data-plane and created no Activity Log event. Exact per-operation diagnostic payload content remains
untested.

**Conclusion:** no authorization bypass. Do not publish the low-value hub-child scope issue as an
attack. The useful verified update is that a disclosed Web PubSub key controls Chat roles and room
membership, and that exact `chat/room/read` is verb-separated from `chat/room/write` at the supported
parent Web PubSub resource scope.

**Teardown:** deleted all three remaining test role assignments, the ACI, UAMI, custom role, and RG
(which removed the Web PubSub service, hubs, linked persistent storage, storage account, and Chat
test data). Removed the `webpubsub` CLI extension that the test installed. Confirmed no `htrc-*`
groups/resources, matching custom roles, test assignments, or extension remain. The pre-existing
`Microsoft.SignalRService` provider registration remains `Registered`.

Final read-only inventory queries returned empty results for `htrc-*` resource groups/resources,
custom roles containing `26926` or the test role name, assignments scoped to the deleted RG, and the
`webpubsub` extension. Provider state returned only `Registered`.

Official references:

- <https://learn.microsoft.com/en-us/azure/azure-web-pubsub/chat-howto-enable-chat>
- <https://learn.microsoft.com/en-us/azure/azure-web-pubsub/chat-reference-sdk-and-rest>
- <https://learn.microsoft.com/en-us/rest/api/webpubsub/controlplane/web-pub-sub-persistent-storages/list?view=rest-webpubsub-controlplane-2025-12-01-preview>
