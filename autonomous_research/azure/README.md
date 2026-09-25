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
| 2026-09-25 | Cosmos DB | Resource-token **irrevocability** vs rotation / permission-delete / user-delete / TTL | **WORKS — new finding** — a minted `Read` token kept reading after primary rotated 3× + secondary 1×, after its `permission` was deleted (>10 min), and after its `user` was deleted. It finally died **exactly at its 1h TTL** (403 "not valid at the current time", start/expiry 1h apart). So the token is effectively irrevocable until TTL; corrected the wiki's wrong "rotation/revoke invalidates tokens" guidance → real containment = data-plane offline or wait out TTL; mint short TTLs. | Yes (both RGs deleted) |
