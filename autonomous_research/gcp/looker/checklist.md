# Looker — research checklist

Last reviewed: 2026-09-28

## Completed

- [x] Separate Google Cloud IAM roles/permissions from Looker application roles, model sets, and content access.
- [x] Reconcile Google OAuth admission and Admin-via-IAM semantics.
- [x] Verify `allowedEmailDomains`, OAuth client, and public-IP update semantics.
- [x] Verify stable export CLI/REST shape, service-agent object/bucket-policy/key dependencies, CMEK restriction, and LRO status-read boundary.
- [x] Verify modern hosted API port/path and API3 login body/header syntax.
- [x] Verify inline query, saved Look, SQL Runner create/run endpoints, permission dependencies, and result limits.
- [x] Verify DB connection/API3 schemas do not return the old claimed secrets.
- [x] Reconcile exact documented Looker application audit methods/classes/defaults and downstream Storage/KMS telemetry.
- [x] Remove destructive-only, duplicate persistence, metadata-only backup, and unsupported credential-theft claims.
- [x] Run focused Markdown, shell, reference, URL, and diff validation without cloud mutation.

## Safe future validation

- [ ] On a disposable Looker test instance, invoke `ExportInstance` with the minimum custom role and inspect whether a Cloud Audit entry is emitted, its exact `protoPayload.methodName`, class, request redaction, and whether LRO completion produces a second entry. The current official audit table omits this method.
- [ ] On a non-CMEK disposable instance, confirm that an export key in another attacker-controlled project is accepted when only the Looker service agent has encrypt permission; immediately delete the export artifact and all temporary IAM grants/key material.
- [ ] With disposable least-privilege Looker roles, confirm the exact API denial/success matrix for `run_inline_query`, `run_look`, `create_sql_query`, and `run_sql_query`, including model sets, access filters, folder access, and download limits.
- [ ] Compare API query activity with Cloud Audit Data Access disabled/enabled, `ContentAccess`/instance logs, System Activity history, and downstream BigQuery/database logs.
- [ ] Confirm one-time export content and recovery boundaries without inspecting production data: excluded OAuth tokens, write-only connection secrets, BigQuery data treatment, and instance-CMEK key constraint.

## Guardrails for future live work

- Use only a disposable instance and synthetic data; a one-time export causes downtime and can take hours.
- Pre-create an empty non-Requester-Pays folder and record every Storage/KMS IAM binding before the test.
- Keep the destination and key in dedicated disposable projects if cross-project behavior is under test.
- Remove service-agent bucket/key grants, delete exported objects/buckets/keys, and verify no scheduled export configuration was introduced.
- Never use import, delete, restart, or production database write statements for validation.
