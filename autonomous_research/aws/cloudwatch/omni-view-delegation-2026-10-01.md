# CloudWatch Omni mutable-view delegation audit — 2026-10-01

## Result

Verified an expected privilege-escalation composition for direct IAM callers: a principal with view-scoped `cloudwatch:GetRecords`, query actions and either `cloudwatch:CreateView` on `view/*` or exact-view `UpdateView` can create/redefine a view that selects raw `logs.default` records. The query path authorizes the synthetic `dataset/view.<name>` resource and does not re-evaluate the caller against `dataset/default`.

This is published as a dangerous mutable security-definer view, not an AWS defect. A view is intentionally a reusable query boundary, and `UpdateView` deliberately grants control over its definition. The surprising explicit-Deny behavior is security-relevant for least-privilege design, but no undocumented API or malformed authorization decision was needed.

## Live authorization matrix

| Test | Result |
| --- | --- |
| Query `logs.default` with query actions and no `GetRecords` | Denied on exact `arn:aws:cloudwatch:us-east-1:228478051196:dataset/default` |
| Query `view.ht_authz_*` with no `GetRecords` | Denied on synthetic `arn:aws:cloudwatch:us-east-1:228478051196:dataset/view.ht_authz_*` |
| Grant `GetRecords` on `dataset/default` but query the view | Still denied on the synthetic view Dataset, proving the resources are distinct |
| Exact returned view ARN + `UpdateView`, with explicit `Deny GetRecords` on `dataset/default` | Successfully replaced the view definition with `SELECT * FROM "logs.default" LIMIT 100` |
| Direct bounded raw query under that explicit deny | Denied on `dataset/default` |
| Bounded query through a raw-record view with only view-Dataset `GetRecords` | Completed and returned 15 real alert-history records (`15,603` bytes scanned, 15 scanned/matched) |
| `CreateView` on `arn:aws:cloudwatch:us-east-1:228478051196:view/*` plus exact chosen view-Dataset read | Created a raw-record view without default-Dataset read, Get/List, domain, space or grant permission; bounded read returned two real rows while scanning 15 |

The successful reader had no `GetView`, `ListViews`, access-grant, domain or space permission. The final test used:

- query-session/start/result/stop actions on `*`;
- `cloudwatch:GetRecords` only on `arn:aws:cloudwatch:us-east-1:228478051196:dataset/view.ht_bounded_<id>`;
- an explicit deny on `arn:aws:cloudwatch:us-east-1:228478051196:dataset/default`.

The separate updater test used `cloudwatch:UpdateView` only on the exact returned ARN:

`arn:aws:cloudwatch:us-east-1:228478051196:view/view.ht_scope_<id>/<uuid>`

The command identifies a view by name, but IAM accepted that full name-plus-UUID resource. No list/get action was required when the name and ARN were already known.

## Interpretation and limits

- This is a direct-IAM resource-scope escalation: a role intended to see a bounded view can broaden it when also trusted to update that view.
- It is not proof that view mutation bypasses an Omni access grant's row-level `dataScope`; no domain/grant existed during the direct-IAM read.
- The view can select logs or traces available to the account/Region Dataset, but it does not grant access to workloads or data never ingested.
- `CreateView` provides a self-created broker when its generated-ARN permission and the chosen synthetic view-Dataset read are both granted. Omitting tags kept the live minimum free of `TagResource`.
- A static aggregate view without `@timestamp` produced a schema error when queried through the standard time-range path. This was a query-shape issue, not an authorization failure.

## CloudTrail

- `UpdateView` was a default management write with `eventSource: cloudwatch.amazonaws.com` and `readOnly:false`.
- Both request and response retained the complete replacement definition: `SELECT * FROM "logs.default" LIMIT 100`.
- Direct and view-backed query calls were management events. As in the foundational audit, `StartTelemetryQuery` hid the submitted outer SQL as sensitive and result rows were not present in Event History.
- The successful result response itself included row data and scan statistics, including `bytesScanned`, `recordsScanned` and `recordsMatched`.

## Cleanup

Every `view.ht_authz_*`, `view.ht_scope_*`, `view.ht_bounded_*` and `view.ht_create_*` fixture was deleted, all query sessions were stopped through cleanup, and every matching `ht-omni-view-*` IAM role/policy was removed. Final USER-view and matching-role inventories were empty. No domain, space, access grant, telemetry forwarding, compute or third-party resource was created.
