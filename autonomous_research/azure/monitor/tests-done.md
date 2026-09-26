# Monitor — Tests Done

Wiki: `az-monitor-post-exploitation.md` (+ Log Analytics pages), unauth `az-monitor-alert-phishing`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | App Insights instrumentation key / live-token abuse | data-plane | **WORKS** (5 primitives lab-verified, commit 03e90018b) |
| 2 | Action-group callback abuse | `actionGroups/write` | **WORKS** |
| 3 | Alert linked-auth abuse | alert write | **WORKS** |
| 4 | `dataCollectionRules/write` AMA file exfil | `dataCollectionRules/write` + `dataCollectionRuleAssociations/write` (+ table/DCE write to build the sink) | **WORKS — lab-verified 2026-09-25** |
| 5 | `dataCollectionRules/data/write` forge logs (modern Entra/DCR Logs Ingestion API) | Monitoring Metrics Publisher on the DCR (+ setup: DCE/DCR/table write) | **WORKS — lab-verified 2026-09-25** |
| 6 | `autoscale`/`logProfiles` teardown / purge notes | those actions | DOC-ONLY |

**Lab record (test, 2026-09-25 — Entra/DCR log forgery):** RG `htrc-logforge`, workspace `htrcws11547`,
DCE `htrcdce15941`, DCR `htrcdcr` (immutableId `dcr-e2f8f501f2be416ea919744db1f413ca`), custom table
`HTForge_CL` (cols TimeGenerated/Actor/Message/SrcIp), stream `Custom-HTForge_CL`, `transformKql: source`.
Granted the caller (a **service principal** — this session's identity; use `--assignee-principal-type
ServicePrincipal`) **Monitoring Metrics Publisher** (`3913510d-42f4-4e42-8a64-420c390055eb`) on the DCR.
`POST <DCE.logsIngestion.endpoint>/dataCollectionRules/<immutableId>/streams/Custom-HTForge_CL?api-version=
2023-01-01` with a `https://monitor.azure.com` Entra token + attacker-chosen rows → **HTTP 204**. Rows became
queryable (`HTForge_CL | count` = 2) after ~4 min first-time `_CL` lag, fields exactly as injected
(`Actor=legit-admin@victim.com`, `SrcIp=10.0.0.5`). KEY POINT: **no workspace shared key involved** — auth is
the Entra token + DCR role, so this bypasses the shared-key/`disableLocalAuth` hardening that stops the legacy
Data Collector API injection already on the wiki. DCR-based custom-table columns keep their declared names (no
`_s` suffix, unlike the legacy path). Wiki: added a "Log forgery via the modern Logs Ingestion API" section +
Logs-generated block to `az-log-analytics-privesc.md`. **Teardown:** `az group delete htrc-logforge`.

**Lab record (test, 2026-09-25 — AMA custom-text-log file exfil):** RG `htrc-amaexfil`, VM `htvm`
(Ubuntu 22.04 B1s, **no public IP**), cloud-init seeded `/var/log/htapp/app.log` with fake secret lines
(`db_password=HT-EXFIL-PROOF-htvm token=…`) every 20s. Built workspace `htwsexf`, DCR-based custom table
`HTAppLog_CL` (`TimeGenerated`/`RawData`), DCE `htdce`, and DCR `htdcr` with a **`logFiles` data source**
(`filePatterns:["/var/log/htapp/*.log"]`, `format:text`, `settings.text.recordStartTimestampFormat: "ISO 8601"`,
stream `Custom-HTAppLog_CL` → workspace, `transformKql: source`); associated to the VM via DCRA `htdcra`.
AMA tailed the file and shipped each line verbatim → `HTAppLog_CL | where RawData contains 'HT-EXFIL-PROOF'`
returned **8** rows, `RawData` = the whole raw line (secrets intact), queryable ~4–5 min after AMA pulled
the config. **KEY GOTCHA:** the VM must have a **managed identity** — AMA authenticates to Azure Monitor as
the VM MI; with none, `mdsd.err` shows `Failed to get MSI token from IMDS` and `config-cache/configchunks`
stays empty (nothing ships). Not an attack limit (production AMA-monitored VMs always have an MI); in-lab we
had to `az vm identity assign` first, then restart `azuremonitoragent`. Wiki: added a lab-verified TIP to the
`dataCollectionRules/write` file-exfiltrator section of `az-monitor-post-exploitation.md`. **Teardown:**
`az group delete htrc-amaexfil` (removes VM + system MI + workspace + DCE + DCR).

**Teardown:** App Insights test resources deleted; `htrc-logforge` deleted; `htrc-amaexfil` deleted. No residue.
