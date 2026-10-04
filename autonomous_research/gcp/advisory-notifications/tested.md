# Advisory Notifications — tested and documented research

Last reviewed: 2026-09-28

## Scope and evidence

- Reviewed the current v1 REST/RPC discovery surface, settings and notification schemas, official opt-in/out guidance, IAM role definitions, audit-method catalog, Sensitive Actions documentation, and current local predefined-role output.
- Confirmed the shared lab initially had `advisorynotifications.googleapis.com` disabled. Two bounded attempts temporarily enabled it and polled project-level v1 `getSettings`; the service returned HTTP 500 on the first attempt and HTTP 500 followed by 503 `UNAVAILABLE` on six polls in the second. No settings document was returned, so no opt-out PATCH was sent.
- Each attempt disabled the API again. Final Service Usage inspection shows it disabled, no matching service account exists, and Cloud Asset finds only the normal disabled Service Usage registry resource. No notification or settings document was returned, and no notification, setting, IAM policy, contact, logging configuration, or other Advisory Notifications product resource was changed.
- The mandatory-type rejection probe therefore remains unresolved. Retrying blindly in the shared lab has little value; use an already-operational disposable Advisory Notifications parent so an unavailable backend is not confused with validation behavior.

## Corrections made

- Removed the false recipient-redirection claim. Current settings contain only a notification-type map of `enabled` booleans, plus resource name and required etag. Recipient routing belongs to Essential Contacts.
- Replaced the invalid `enablement:"DISABLED"`/`updateMask` request with a full, etag-preserving v1 settings PATCH using `notificationSettings.<TYPE>.enabled=false`.
- Bounded suppression to the optional Sensitive Actions and Threat Horizons types. Security and Privacy Advisory and Security MSA are mandatory and cannot be opted out.
- Recorded that existing notifications remain and that Sensitive Actions platform logs and Security Command Center findings are independent of Advisory Notifications opt-out.
- Corrected notification read audit permissions from `DATA_READ` to `ADMIN_READ`, retained the default-off Data Access classification, and used exact stable v1 list/get/settings method names.
- Recorded the official catalog mismatch: stable v1 exposes `UpdateSettings`, but the current audit table enumerates only v1alpha `UpdateSettings`. The `ADMIN_WRITE` permission contract supports Admin Activity, but the stable-call emitted method name remains a live-capture gap.
- Documented that `notifications.list` with `view=FULL` returns full messages and structured CSV attachments, while `get` is unnecessary for collection-wide retrieval.

## Retained techniques

- Full notification and attachment enumeration as high-stealth, potentially sensitive post-exploitation reconnaissance.
- Organization-level Sensitive Actions opt-out as bounded, low-stealth defense evasion. It is not privilege escalation or access persistence and does not blind mandatory or independent channels; Threat Horizons suppression alone does not clear the bar for a separate technique.

## Live result

- **Expected-functionality probe, unresolved:** the public v1 settings API did not initialize for the lab project after Service Usage reported enablement complete. Repeated `getSettings` calls returned only server-side 500/503 responses. This is not a demonstrated security issue: no authorization boundary failed, no notification data leaked, and the mandatory setting was never submitted.
- **Cleanup:** both enablements were paired with successful disables; final enabled-service and service-account checks are clean. The remaining Cloud Asset service record represents the disabled API registration, not a running test asset.

## No-garbage decisions

- No privilege-escalation page: the service has no resource creation, execution, credential mint, policy write, or deputy path that yields permissions the caller did not already have.
- No persistence page: disabling a delivery setting is durable configuration tampering but does not preserve attacker access. Essential Contacts already covers the separate out-of-band recipient foothold.
- No unauthenticated technique: all current v1 operations require OAuth and parent-scoped IAM.

## 2026-09-28 — independent cross-review

- Revalidated the v1 discovery schema: `Settings` requires the complete `notificationSettings` map and current `etag`; `UpdateSettings` takes the `Settings` body directly, has no update mask, and returns `Settings` rather than an LRO. The example now refuses to create or overwrite an absent or already-disabled Sensitive Actions entry, restores the original full map with the etag returned by the controlled write, and removes its local temporary documents after a successful restore.
- Retained optional-delivery suppression only because organization-level Sensitive Actions email is routed to Security Essential Contacts, or to Organization Administrators when no such contacts exist. This is a bounded defense-evasion primitive. Threat Horizons is strategic reporting and remains context rather than a distinct technique.
- Confirmed `FULL` is part of `ListNotifications` and has no extra attachment permission:
  `advisorynotifications.notifications.list` is the sole IAM permission on that request. The response embeds message bodies and structured CSV attachment rows.
- Confirmed the current audit catalog lists stable v1 read methods as non-LRO `ADMIN_READ` Data Access and still omits stable v1 `UpdateSettings`, while the v1alpha update remains cataloged as `ADMIN_WRITE`.
- A read-only cleanup check found the API disabled and zero matching Google-managed service accounts. Service Usage Admin Activity contains exactly two enable LROs and two matching disable LROs; each operation has its normal initial/final entries. No API or identity state was changed by this review.
