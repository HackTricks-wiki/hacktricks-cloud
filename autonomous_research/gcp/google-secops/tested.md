# Google SecOps post-exploitation research ledger

## 2026-09-28 — full documentation audit

This audit used current official Google SecOps REST, IAM, rule-management, and audit-logging documentation plus local Google Cloud SDK 586.0.0 help/source. The SDK has no `gcloud chronicle` surface. No tenant, project, API state, or cloud resource was read or changed.

### Retained techniques

1. **UDM and raw-log search.** Stable UDM search is `GET /v1/{instance}:udmSearch`; raw-log search is `POST /v1alpha/{instance}:searchRawLogs`. Permissions are independent. Results remain bounded by retention and data access scopes.
2. **Rule-deployment disable/alert suppression.** `chronicle.ruleDeployments.update` can set `enabled=false` or `alerting=false`; these have different effects and require a field mask.
3. **Rule revision tamper.** `chronicle.rules.update` can replace complete YARA-L text and creates a revision. Prior revisions and compilation metadata remain as evidence and a recovery path.
4. **Reference-list/data-table poisoning.** `chronicle.referenceLists.update` replaces list entries; `chronicle.dataTableRows.create` appends a row. Offensive value exists only where a deployed rule treats the inserted value as trusted or excluded.
5. **Feed disable.** The dedicated `chronicle.feeds.disable` method changes a feed to `ARCHIVED` and stops later ingestion without deleting already ingested events.
6. **Case closure.** `chronicle.cases.close` can bulk-close known numeric case IDs with a valid reason after SOAR migration to a customer-managed project. Evidence remains, and future workflow can reopen or recreate cases.

### Material corrections

- Replaced legacy search calls with the stable v1 UDM endpoint and exact v1alpha raw-search POST body.
- Removed the claim that SecOps Data Access audit logging is off by default. Google documents it as enabled by default; explicit audit permission-type configuration is needed to populate UDM/raw query text.
- Replaced guessed service/method strings with exact public RPC names from current REST pages and documented the audit guide's `v1main` method-name namespace caveat.
- Corrected rule-deployment semantics: disabling stops continuous execution; disabling alerting alone leaves detections but prevents their promotion to alerts.
- Replaced generic `dataTables.*` with the exact row-create permission and schema, and made lookup directionality a prerequisite rather than assuming every list is an allowlist.
- Replaced feed update/delete with the dedicated disable method and bounded it to one feed and future ingestion.
- Replaced vague `chronicle.soar*` claims with the public case bulk-close API, exact permission, request fields, migration prerequisite, and retained-case-evidence boundary.

### Rejected or folded hypotheses

- **Retention/data deletion:** not retained because the current public REST catalog does not expose a supported retention-reduction or bulk data-deletion method with a verifiable permission/request.
- **Playbook disable:** not retained because the original heading supplied no public Chronicle REST method, exact permission, or auditable request. Case closure is documented and independently useful.
- **Rule/feed deletion:** folded as destructive duplicates. Rule update/deployment disable and feed disable provide the useful effect with narrower, reversible scope.
- **`rules.update` plus `rules.delete`:** split in favor of update only; delete has force-dependent retrohunt/detection consequences and is unnecessary for the retained defense-evasion primitive.
- **Viewer role guarantees:** removed from technique minimums. Exact permissions and effective data access scopes are authoritative; predefined role contents can change and basic roles can be broad.

### Telemetry conclusions

- Rule, rule-deployment, reference-list, and feed configuration writes are Admin Activity and always on. Data-table row creation, search, and case-data operations are Data Access. Google documents SecOps Data Access logs as enabled by default and says disabling them requires a SecOps representative.
- Search query text requires explicit Chronicle API audit configuration selecting Admin Read, Data Read, and Data Write; an absent query string does not prove the search method was unaudited.
- The public REST RPC namespace is `google.cloud.chronicle.v1`, while Google's emitted UpdateRule example uses `google.cloud.chronicle.v1main`; tenant output must be checked before hard-coding method filters for other operations.

## 2026-09-28 — independent cross-review

- Confirmed the six retained primitives and their v1/v1alpha HTTP shapes against the current REST catalog; no additional low-value heading was restored.
- Corrected the permission-to-method mapping for reference-list writes to `ReferenceListService.UpdateReferenceLists` (plural), while retaining the public v1 versus emitted `v1main` warning.
- Removed the JSON body from feed disable because the method explicitly requires an empty request body.
- Added the documented non-atomic boundary for multi-field RuleDeployment updates.
- Tightened bulk case-close prerequisites to include `rootCause` as required by the method contract, and corrected the retained-evidence field to `closureDetails` and its manual-close marker.
