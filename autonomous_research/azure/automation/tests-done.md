# Automation — Tests Done

Wiki: `az-automation-account-persistence.md` / privesc, unauth `az-automation-webhooks-unauth`.

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | **Watcher tasks** — sub-schedule-floor recurring execution (`executionFrequencyInSeconds=60`) | `automationAccounts/watchers/write` | **WORKS (corrected)** | Verified `=60` accepted. **CORRECTED the common ATRM claim**: `watchers/write` **IS** logged (Activity Log Started+Succeeded). Toy watcher runbook failed (no `Start-AutomationWatcherLoop`) so did NOT overclaim an execution loop. |
| 2 | Automation webhook = unauth-by-design POST → runbook under sub-privileged MI | none (unauth, holds webhook URL) | **DOC-ONLY** | ATRM AZT503.3; on unauth page. |
| 3 | Runbook RCE as Run-As / MI | `runbooks/write`+`draft/publish`+`jobs/write` | **DOC-ONLY** | Covered pre-audit. |

**Skipped (justified):** Update Management (retired 31 Aug 2024), extension Hybrid Worker (needs VM,
overlaps), Run-As cert (legacy retired), cert-asset dump (already covered).
**Teardown:** `htrcaa30648` and related RG deleted. No residue.
