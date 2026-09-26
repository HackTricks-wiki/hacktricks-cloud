# Web PubSub Chat — Candidate Attacks

- [x] Test whether a custom `Microsoft.SignalRService/WebPubSub/chat/room/read` DataAction assigned
      at one `WebPubSub/hubs` child scope can read rooms in that hub but not a sibling hub. Require a
      same-hub 200 positive control before grading the sibling request. **REFUTED 2026-09-26:** the
      hub-child assignment never produced a positive control. The supported parent-resource scope
      authorized both hubs; no cross-hub bypass occurred.
- [x] Confirm read/write verb separation: `chat/room/read` must not authorize room creation or
      modification requiring `chat/room/write`. **PASS 2026-09-26:** both reads returned 200 while a
      room PUT returned 403 naming `chat/room/write`.
- [x] Verify whether a listed Web PubSub key reaches the preview Chat administration plane.
      **PASS 2026-09-26:** key-signed JWTs created a custom room role and assigned it to a member.
- [ ] Repeat the scope and verb matrix for `chat/user`, `chat/conversation`, `chat/message`, and
      `chat/role`; verify that each documented DataAction maps only to its intended REST routes.
- [x] Test whether built-in `Web PubSub Service Owner` (`WebPubSub/*`) expands to the new preview Chat
      DataActions. **PASS 2026-09-26:** a correctly assigned object ID read both hubs after normal
      propagation. An earlier control accidentally used the app ID and was discarded.
- [ ] Measure resource diagnostic coverage for Chat room, user, message, conversation, and role
      operations. Activity Log must not be treated as data-plane evidence.
- [ ] Check whether `persistentStorages/write` can link storage outside the Web PubSub resource's
      subscription/tenant, or accept a storage account the service identity cannot access.
- [ ] Check whether `hubs/write` permits switching an existing hub to Chat and referencing a linked
      persistent storage without `persistentStorages/read`.
