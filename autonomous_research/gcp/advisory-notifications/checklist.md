# Advisory Notifications research checklist

## Completed documentation checks

- [x] Enumerate current v1 organization/project notification and settings resources.
- [x] Verify notification FULL/BASIC views, pagination, attachment representation and minimum IAM.
- [x] Verify current settings schema, etag requirement and lack of recipient fields.
- [x] Separate optional from mandatory notification types.
- [x] Separate Advisory Notifications opt-out from Essential Contacts routing, Sensitive Actions
      platform logs and Security Command Center findings.
- [x] Verify predefined Admin/Viewer contents and exact stable read audit methods.
- [x] Record the stable v1 versus cataloged v1alpha `UpdateSettings` telemetry gap.
- [x] Remove recipient-redirection, all-alert suppression and invalid request-shape claims.
- [x] Independently verify the full-map/no-update-mask v1 schema, organization-only Sensitive
      Actions recipients, no extra permission for FULL attachments, and non-LRO audit boundaries.
- [x] Reconfirm cleanup read-only: two enable/disable LRO pairs, API currently disabled, and no
      Advisory Notifications service agent.

## Safe future validation

- [ ] In an already-operational disposable organization/project with synthetic notification state,
      capture stable v1 `GetSettings` and `UpdateSettings` entries. Resolve the exact emitted update
      method name and request redaction, then restore only the controlled optional type using
      optimistic concurrency. Do not repeat enable-and-poll in the shared lab unless backend
      availability changes; the 2026-09-28 attempts returned only HTTP 500/503 and were cleaned up.
- [ ] Attempt to disable each mandatory type in a disposable parent and capture the rejection without
      changing state. Do not run this against an operational security-notification parent.
- [ ] Enumerate `view=BASIC` versus `view=FULL` under a custom role containing only
      `notifications.list`; confirm that attachment rows need no additional permission and record
      pagination behavior without retaining sensitive content.
- [ ] Compare project- and organization-level notifications for inherited/duplicated delivery and
      verify that a project-scoped reader cannot enumerate organization notices.
- [ ] With Sensitive Actions and Security Command Center already configured in a disposable org,
      opt out only of the Advisory Notifications delivery channel and confirm platform logs/findings
      remain. Restore settings immediately.

## Cleanup invariant

- [ ] Save the complete settings document and etag before any future mutation.
- [ ] Never alter mandatory notices, real Essential Contacts, or a production SOC delivery path.
- [ ] Restore only the controlled optional field with current concurrency state; verify all four
      notification-type values after cleanup and retain no notification contents or attachments.
