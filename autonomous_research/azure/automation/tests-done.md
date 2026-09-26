# Automation — Tests Done

Wiki: `az-automation-account-persistence.md` / privesc, unauth `az-automation-webhooks-unauth`.

| # | Technique | Min perms | Status | Notes |
|---|-----------|-----------|--------|-------|
| 1 | **Watcher tasks** — sub-schedule-floor recurring execution (`executionFrequencyInSeconds=60`) | `automationAccounts/watchers/write` | **WORKS (corrected)** | Verified `=60` accepted. **CORRECTED the common ATRM claim**: `watchers/write` **IS** logged (Activity Log Started+Succeeded). Toy watcher runbook failed (no `Start-AutomationWatcherLoop`) so did NOT overclaim an execution loop. |
| 2 | Automation webhook = unauth-by-design POST → runbook under sub-privileged MI | none (unauth, holds webhook URL) | **DOC-ONLY** | ATRM AZT503.3; on unauth page. |
| 3 | Runbook RCE as Run-As / MI | `runbooks/write`+`draft/publish`+`jobs/write` | **DOC-ONLY** | Covered pre-audit. |
| 4 | **Webhook late-binding: URL survives runbook content swap** (silent payload replacement) | `webhooks/*` (create) + `runbooks/write`+publish (swap) | **WORKS — new finding** | lab-verified 2026-09-25 |

**Lab record (test, 2026-09-25 — webhook content-swap persistence):** RG `htrc-aawh`, account `htrcaawh2357`,
PowerShell runbook `htrbwh`. `az automation webhook` is not in this CLI build, so the webhook was minted via
REST: `POST .../webhooks/generateUri` (returns the 143-char token URL **once**) then `PUT .../webhooks/htwh1`
with `{isEnabled, uri, expiryTime, runbook.name}` — corroborating the wiki's `webhooks/*` wildcard requirement
(generateUri = `webhooks/action`, distinct from the `webhooks/write` PUT). Confirmed a later `GET` on the
webhook returns an **empty `properties.uri`** (defender cannot recover the URL). Published runbook body v1
(`Write-Output "VERSION=1-BENIGN"`), invoked the URL (`202` + JobIds) → job output = `VERSION=1-BENIGN`.
Then `runbook replace-content` + `publish` swapped the body to `VERSION=2-SWAPPED-MALICIOUS` (webhook object
untouched — same name, token, URL, expiry). Invoked the **identical URL** again → job output =
`VERSION=2-SWAPPED-MALICIOUS`. **Conclusion:** a webhook binds to the runbook by name, executing whatever is
*currently published*; the payload can be swapped post-creation with only a `runbooks/write`+publish (ordinary
maintenance) and no second `webhooks/write`. Containment: re-publishing clean content neutralises the URL
without finding it, but only until the attacker republishes; durable eviction = delete the webhook/runbook or
disable the account. Wiki updated (`az-automation-accounts-persistence.md` "Schedules and webhooks": added a
lab-verified WARNING). **Teardown:** `az group delete htrc-aawh`.

**Skipped (justified):** Update Management (retired 31 Aug 2024), extension Hybrid Worker (needs VM,
overlaps), Run-As cert (legacy retired), cert-asset dump (already covered).
**Teardown:** `htrcaa30648` and related RG deleted. No residue.
