# Cloud Runtime Configurator research ledger

## 2026-09-28 — current-contract and live no-residue audit

- Reconciled the v1beta1 REST discovery document, current IAM role index, variable guide, Deployment
  Manager shutdown schedule, Google Cloud audit-supported-services catalog, local gcloud beta help,
  and an authorized disposable live fixture.
- Retained one config-scoped privilege escalation: `runtimeconfig.configs.setIamPolicy` can add a
  controlled principal to `roles/runtimeconfig.admin` on the target config. This expands a policy-
  write-only delegation into full variable/waiter/policy administration on that config, but it does
  not grant project Owner or permissions on other configs/services.
- Moved the genuinely useful variable-value disclosure into a new post-exploitation page. A known
  path needs `runtimeconfig.variables.get`; enumeration additionally needs config and variable list.
  The `--values` list behavior checks `get` per variable and omits unauthorized values.
- Removed variable poisoning and waiter C2 as standalone privesc headings. Both are expected uses of
  the held permissions, and any stronger effect depends on an external workload-specific consumer.
  Creating an empty config also does not cause an existing workload to trust it.
- Corrected the stale claim that v1beta1 `getIamPolicy` returns HTTP 404. The controlled request
  returned HTTP 200 with an empty direct policy and etag; the official method likewise documents an
  empty policy for an existing config without a direct policy. The book now uses a preservation-safe
  read-modify-write example rather than replacing the full policy with one binding.
- The current IAM index lists variable/waiter `getIamPolicy` and `setIamPolicy` permissions, while
  the current public discovery/API reference exposes policy methods only at config scope. No child-
  resource self-grant was claimed from permission names alone.
- Runtime Config remains Pre-GA and under the legacy Deployment Manager documentation. Deployment
  Manager support ended April 1, 2026; Google says Deployment Manager and its V2 API remain for
  existing customers until the June 30, 2027 shutdown. That notice does not separately name
  `runtimeconfig.googleapis.com`, so the book no longer presents June 30, 2027 as a confirmed
  Runtime Config endpoint shutdown. Current role docs still list GA Runtime Config
  Admin/Editor/Viewer roles.

### Live fixture and cleanup

- The API was already enabled in `gcp-labs-eqd4ny8d`; it was not enabled or disabled for this test.
- Created one uniquely named `ht-runtime-20260928134618` config, confirmed `getIamPolicy` HTTP 200,
  set a direct `roles/runtimeconfig.admin` binding to the already-active project owner principal,
  created/read one synthetic `ht/test-value` variable, and created one short waiter.
- Restored the config's direct policy to empty, deleted the config (cascading its variable/waiter),
  and confirmed a subsequent describe failed because the config was absent. No service account,
  role, project binding, API state, secret, database, network, or billable resource was created.
- A log query covering the run ID and `runtimeconfig.googleapis.com` returned no entry. This is
  decisive for the normally-always-on policy/config mutations in that fixture, but the read result
  alone is bounded because the project had no Data Access audit configuration. The official service
  catalog also omits Runtime Config entirely; the public pages therefore say “no documented/observed
  entry” rather than fabricating method names.

No unexpected authorization failure or cross-tenant boundary was found, so no private vulnerability
report was created.

## 2026-09-28 — independent cross-review

- Rechecked the current Runtime Config REST methods, role index, custom-role support table, local
  beta CLI help, Deployment Manager notice, and Cloud Audit Logs supported-services catalog. No
  cloud state was changed.
- Confirmed the one-privesc/one-post-exploitation split. Config `setIamPolicy` can expand a policy-
  only grant into config-scoped administration, while reading already-authorized variable values is
  data access rather than privilege escalation. Variable poisoning remains consumer-dependent and
  is not a generic third technique.
- Confirmed that both config IAM permissions are currently `TESTING` for custom roles and that
  `roles/runtimeconfig.admin` is GA. `roles/iam.securityAdmin` has config IAM get/set/list but lacks
  the variable and waiter permissions, providing a concrete predefined-role escalation boundary.
- Validated that the policy command preserves all top-level policy fields, existing bindings,
  conditional bindings, version, and etag while merging only into an unconditional Runtime Config
  Admin binding. The raw method replaces the supplied complete policy.
- Corrected the deprecation boundary: June 30, 2027 is explicitly the Deployment Manager/V2 API
  shutdown date. Runtime Config is separately callable and documented, and Google has not published
  a distinct shutdown date for `runtimeconfig.googleapis.com` on the cited page.
- Removed the generic deny/PAB caveat. These policy types only affect permissions in their supported
  contracts; no Runtime Config follow-on permission was established as supported.
- Reconfirmed the audit wording: Google omits Runtime Config from its supported audit-service
  catalog, while the fixture observed no entries. Reads remain phrased as observed rather than as a
  universal guarantee because Data Access logging was not enabled in the fixture.
- Independently rechecked cleanup: describing `ht-runtime-20260928134618` now returns `NOT_FOUND`,
  while the pre-existing Runtime Config API remains enabled. No cleanup mutation was needed.
- A separate persistence page was rejected as low-value duplication. The only durable foothold is
  the same visible config IAM binding already documented as the self-grant; it introduces no second
  credential, delayed re-entry mechanism, or distinct telemetry/cleanup boundary, and reaches only
  one legacy config. If a future technique leaves a consumer-side backdoor that survives removing
  this binding, reassess it separately.
