# Azure Autonomous Research — Test Tracking

This folder is the shared, durable record of **which Azure attack techniques have actually been
tested**, so future agents do not repeat work and know exactly where the frontier is. It is
maintained alongside the HackTricks Cloud wiki audit on branch `hermes/az-services-technique-audit`
(PR #412).

## How this is organized

```
autonomous_research/azure/
  README.md                      <- this file (system + global status)
  <service>/
    tests-done.md                <- every test performed on the service: what worked,
                                    what did NOT and WHY. Confirmed + refuted + can't-test.
    checklist.md                 <- candidate attacks NOT yet tested. When an item is
                                    checked, it MOVES OUT of here into tests-done.md
                                    (and, if it works, into the wiki page).
```

## The loop (contract)

1. **Pick** a candidate from a service `checklist.md` (prefer cheap, lab-testable, genuinely-useful
   attacks — never garbage/non-attacks).
2. **Test** it in the lab sub `azure-labs-owCfs7hi` (`7f98c578-1bb0-4c66-99fb-85f39ac0380b`) with the
   **minimum necessary permissions**, in parallel (3–5) where safe.
3. **Record** the result in `<service>/tests-done.md` (worked / didn't + why / couldn't-test + why),
   and **remove** the item from `checklist.md`.
4. If it **works** → add/confirm the technique on the HackTricks Cloud wiki page (min-perms, impact,
   expandable "Logs generated", Stealth on persistence) and update PR #412.
5. **Tear down ALL infra** launched for the test — no residue. Ever.
6. When a service's `checklist.md` is empty → read more, brainstorm more *real* attacks, refill it
   (no duplicates of anything already in tests-done.md or the wiki).

## Test-status legend (used in tests-done.md)

- `WORKS` — lab-verified in `azure-labs-owCfs7hi`; behaviour confirmed; on the wiki.
- `REFUTED` — tested and did NOT work / was mitigated; documented so nobody retries it.
- `DOC-ONLY` — technique is real and on the wiki, but confirmed from ARM op catalog + vendor docs,
  not live-fired (cost/quota/privilege wall). The wall is named.
- `CANT-TEST` — blocked by a lab wall (see below); documented from theory per the /goal.

## Known lab walls (azure-labs-owCfs7hi)

- **App Service / Web compute quota = 0** on every SKU (F1/S1/…): cannot provision Web App plans.
  Use a **Consumption Function App** instead where possible.
- **Batch pool quota = 0** (cannot allocate compute nodes).
- **SQL logical server provisioning blocked** (no live T-SQL path; no usable outbound 1433).
- **No Microsoft Graph directory write**: cannot create Entra app registrations / service principals /
  directory objects. Derive min-perms from the exact ARM action Azure requires instead.
- **Key Vaults with purge protection cannot be manually purged** — Azure auto-purges on schedule.
- Cost gate: skip anything that would cost **> $5 / 30 min** (or whose deletion lock raises cost).

## 0day boundary

If a live technique escapes CLIENT infra into Azure's own backend (hypervisor/host escape,
cross-tenant, Azure-operated hosts) it is a **0day** → private MSRC report, **never** the public wiki.
See memory `azure-0day-boundary-rule`.

## Global status (2026-09-24)

The Azure privesc / post-exploitation / persistence / env-var-RCE / unauthenticated-access audit is
**maintenance-complete** at the useful-primitive level across phases 1–6 (see memory
`azure-technique-audit-progress`, `azure-unauth-axis-progress`, `azure-envvar-rce-audit-complete`).
This tracking folder **backfills** the verified test history and captures the remaining frontier: the
many techniques flagged **UNVERIFIED** on the wiki (real, documented, but never live-fired) — those
are the live checklist items, prioritized by whether the lab can actually fire them cheaply.

## Test loop log

| Date | Service | Test | Result | Infra torn down? |
|------|---------|------|--------|------------------|
| 2026-09-24 | Key Vault | `enableRbacAuthorization` flip (both directions) | **WORKS** — RBAC→policy revives lingering policy (data read w/ `vaults/write` alone); policy→RBAC = `ForbiddenByRbac` lockout | Yes (vault purged, RG deleted) |
| 2026-09-24 | IoT Hub / DPS | Group-key fleet forgery → arbitrary device foothold | **WORKS** — never-enrolled device `assigned`, enabled in registry, live D2C accepted | Yes (RG deleted; hub+DPS gone) |
| 2026-09-24 | Cosmos DB | Native `sqlRoleAssignments` self-grant + Activity-Log check | **WORKS** — grant works with no `Microsoft.Authorization` change; `sqlRoleAssignments/write` **is** logged (~2-3 min) but NOT as an Azure-RBAC event = SOC blind spot; data-plane use unlogged. Wiki already correct. | Yes (RG deleted) |
| 2026-09-24 | VMs/Compute | Run Command RCE min-perm + log footprint | **WORKS** (re-confirm) — root RCE via ARM (no SSH/IP); min perm `runCommand/action`; action logged, script body NOT logged. Wiki already verified. | Yes (RG deleted) |
| 2026-09-24 | AI Search | WebApiSkill SSRF + MI-token attach (indep. repro) | **WORKS (SSRF)** — outbound call from `CognitiveSearch/WebApiSkill` UA; **token exfil CONSTRAINED** — `authResourceId` rejects first-party audiences. Wiki already covers (d1527e426). | Yes (RG deleted) |
| 2026-09-25 | Monitor/Log Analytics | Log forgery via the modern Entra/DCR Logs Ingestion API (no shared key) | **WORKS — new finding** — built DCE+DCR+custom table, granted self *Monitoring Metrics Publisher* on the DCR, POSTed forged rows with only a `monitor.azure.com` Entra token → 204; queryable (count=2) in ~4min, fields as injected. Bypasses the shared-key/`disableLocalAuth` hardening that stops the already-documented Data Collector API injection. Added new section + Logs-generated block. | Yes (RG deleted) |
| 2026-09-25 | Service Bus/Event Hubs | Self-minted SAS auth-rule persistence + two-key eviction gap | **WORKS — new finding** — a locally-minted SAS token (HMAC over resource URI, no Entra) sends messages (201); regenerating **only the primary key** kills the primary-signed token but the **secondary-signed token still works** — must rotate BOTH keys (or delete the rule; ~6s) to evict. RBAC removal does nothing (SAS has no identity). Same model on Event Hubs. Added a new persistence section w/ eviction matrix. | Yes (RG deleted) |
| 2026-09-25 | ACR | Repository-scoped token persistence: independence from admin account + eviction matrix | **CONFIRMED (additive)** — a scoped token authenticates via `oauth2/token` with pure HTTP Basic (no Entra); survives `az acr credential renew` AND `--admin-enabled false` AND RBAC removal. Real eviction: `token update --status disabled` (200→401 ~9s), `token credential generate` (old dies now, new ~51s), or delete token/scope-map. ARM-revocation angle was already documented; admin-independence + matrix is new. Added lab-verified WARNING. | Yes (RG deleted) |
| 2026-09-25 | App Svc/Functions | Publishing-credential persistence: Entra-independence + which eviction lever works | **CONFIRMED (novel persistence/eviction nuance)** — on a Windows Consumption FA, once SCM basic-auth is enabled the site publishing creds give Kudu `/api/command` RCE via pure HTTP Basic (no token/MFA/CA); **role removal does NOT evict** (carries no Azure identity) — only flipping `basicPublishingCredentialsPolicies/scm` back to `allow=false` (200→401 in ~12–24s) or rotating creds does. Default posture confirmed `allow=false`. Added lab-verified WARNING (privesc mechanism was already documented). | Yes (RG deleted) |
| 2026-09-25 | Automation | Does a webhook URL survive runbook **content replacement** (payload swap)? | **WORKS — new finding** — the same untouched webhook URL ran `VERSION=1-BENIGN`, then after `replace-content`+`publish` swapped the body it ran `VERSION=2-SWAPPED-MALICIOUS`. Webhook binds to runbook by name → late-binding stealth persistence (one `webhooks/write`, payload swapped later as ordinary `runbooks/write`+publish). URI unrecoverable on GET; durable eviction = delete webhook/runbook. Added lab-verified WARNING. | Yes (RG deleted) |
| 2026-09-25 | VMs/Compute | Disk export SAS (`grant-access`) revocation latency | **CONFIRMED** — `revoke-access`/`endGetAccess` kills an outstanding VHD-export SAS (`206`→`403`) within ~8s; otherwise it lives for the full requested duration. Prompt kill switch (contrast: Cosmos token ignores revocation until TTL). Added lab-verified NOTE. | Yes (RG deleted) |
| 2026-09-25 | Storage | SAS revocation matrix — which lever kills which SAS type | **CONFIRMED/new nuance** — account/service SAS dies ~15-30s after key rotation but NOT on role removal; user-delegation SAS SURVIVES key rotation but dies ~20s after removing the delegating principal's RBAC role and ~15s after `revoke-delegation-keys` (UDS is re-authorized against live RBAC per request — opposite of Cosmos token). Added lab-verified matrix to storage persistence page. | Yes (RG + role assignment deleted) |
| 2026-09-25 | Storage | Does SFTP local user survive Shared-Key-disable + key rotation? | **WORKS — new finding** — after `--allow-shared-key-access false` + both keys rotated, the account-key path is dead (control) but the SFTP local user still logs in and uploads. Only disabling SFTP / deleting the local user / deleting the account evicts it. Added lab-verified WARNING to storage persistence page. | Yes (RG deleted) |
| 2026-09-25 | AKS | Does `rotate-certs` actually revoke a leaked `--admin` kubeconfig? | **CONFIRMED** — after `az aks rotate-certs` the API server returns `Unauthorized` to the old client cert even with `--insecure-skip-tls-verify` (naive re-test only shows a misleading client-side CA-trust error); fresh kubeconfig has a new cert serial. Wiki remediation claim holds. Added lab-verified NOTE. Cost note corrected: 1-node B2s free-tier AKS is under the gate. | Yes (RG + MC_ RG deleted) |
| 2026-09-25 | Cosmos DB | Resource-token **irrevocability** vs rotation / permission-delete / user-delete / TTL | **WORKS — new finding** — a minted `Read` token kept reading after primary rotated 3× + secondary 1×, after its `permission` was deleted (>10 min), and after its `user` was deleted. It finally died **exactly at its 1h TTL** (403 "not valid at the current time", start/expiry 1h apart). So the token is effectively irrevocable until TTL; corrected the wiki's wrong "rotation/revoke invalidates tokens" guidance → real containment = data-plane offline or wait out TTL; mint short TTLs. | Yes (both RGs deleted) |
| 2026-09-25 | Monitor | AMA custom-text-log **file exfil** off a monitored VM (`dataCollectionRules/write` + DCRA) | **WORKS — was DOC-ONLY, now lab-verified** — DCR `logFiles` source on `/var/log/htapp/*.log` → AMA tailed the host file and shipped the raw secret lines (`db_password=…`) into attacker-readable `HTAppLog_CL` (8 rows, full line intact) ~4-5 min after config pull; no login/RCE on the box. **Gotcha:** the VM must have a managed identity (AMA auths as the VM MI; none → `Failed to get MSI token from IMDS`, empty config-cache) — not an attack limit since production AMA-monitored VMs always have one. Added lab-verified TIP. | Yes (RG deleted; VM+MI+ws+DCE+DCR gone) |
| 2026-09-25 | Logic Apps | Captured request-trigger callback URL survival vs disable/enable + key regen | **WORKS — new finding** — a SAS-signed callback URL invokes the workflow anonymously (200, no token); **disable→enable does NOT revoke it** (400 `WorkflowTriggerIsNotEnabled` only while disabled, 200 again on re-enable), regenerating a **single** access key was insufficient in-window, and rotating **both** keys revoked it only after a **~12–15 min propagation lag** (then 401 `AuthorizationFailed`). Immediate eviction = delete trigger/workflow or leave disabled. Added a lab-verified WARNING to the persistence page. | Yes (RG deleted) |
