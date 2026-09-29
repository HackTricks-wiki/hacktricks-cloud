# Cloud CLI Execution — tested

## 2026-09-29 — remote CLI breadth, authorization boundary, and guardrails

- Resolved the hidden Preview Service Usage identifier as `cloudcli.googleapis.com`; the normal available-services listing did not expose it, but a direct Service Usage lookup returned a valid disabled service and the alternate `cloudcliexecution.googleapis.com` name did not exist.
- Anonymous `tools/list` exposed only the static schemas for `run_gcloud_command` and `run_bq_command`. Both were marked destructive/non-idempotent/non-read-only and accepted optional input files. No project data was returned without invoking a tool.
- A disposable identity with only `resourcemanager.projects.get` and `serviceusage.services.use` successfully described the project directly. Its project `testIamPermissions` response omitted `mcp.tools.call`, and the equivalent remote command was denied specifically on `mcp.googleapis.com/tools.call`. The Owner positive control ran the same command; an unauthenticated call returned HTTP 401. No authorization bypass was found.
- The Owner control also executed a non-mutating `bq ls`, confirming both published tools. A harmless semicolon separator was passed to gcloud as ordinary arguments and rejected, rather than starting a second process. A slash-containing attempt to place an input file under the gcloud configuration directory was rejected by path validation.
- The live command filter was more granular than the guide's broad unsupported-command example:
  `gcloud iam service-accounts list` succeeded, but `gcloud iam service-accounts keys create` was rejected before creating a key. This is useful restriction nuance, not a credential-minting bypass.
- The project had no `mcp.googleapis.com` Data Access audit configuration. Queries for `cloudcli.googleapis.com/mcp`, `cloudcli.googleapis.com`, and the read-only downstream project lookup returned no entries, consistent with the published off-default wrapper contract and the read-only downstream operation.
- Deleted the user-managed key, IAM binding, service account, and isolated credential directory; disabled the API to its prior baseline. The custom role is in GCP's expected soft-deleted state, with no active binding or principal remaining.
