# App Services / Functions — Tests Done

Wiki: `az-app-services-privesc.md`, `az-functions-app-privesc.md`, unauth `az-app-services-functions-unauth`.

**KEY WALL:** azure-labs sub has **0 App Service (Web) compute quota** on all SKUs → cannot provision
Web App plans. Use a **Consumption Function App** where a Functions equivalent exists.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Slot swap to promote attacker code | `sites/slotsswap/action` | DOC-ONLY (quota wall) |
| 2 | Backup exfil | `sites/write`+storage | DOC-ONLY |
| 3 | VNet integration pivot | `sites/config/write` | DOC-ONLY |
| 4 | Kudu process memory dump | Kudu/publish creds | DOC-ONLY |
| 12 | **Publishing-credential persistence: Entra-independent Kudu login survives RBAC removal; only policy-toggle/cred-rotation evicts** | `sites/config.../publishingcredentials` (read creds) + `basicPublishingCredentialsPolicies/write` (enable SCM basic auth) | **WORKS/CONFIRMED — lab-verified 2026-09-25 (Windows Consumption)** |

**Lab record (test, 2026-09-25 — publishing-credential persistence + eviction latency):** RG `htrc-scm`.
Linux Consumption FA (`htrcfa11749`) was a dead end — its Kudu/SCM front-end returns `503` until content is
published, so SCM basic-auth tests aren't feasible there. Created a **Windows** Consumption FA
(`htrcfaw16266`) — full Kudu, SCM live immediately. Findings (all curl-verified with the credential-embedded
`scmUri`, no Azure token in the request):
- **Default posture (confirms wiki):** fresh FA ships with BOTH `basicPublishingCredentialsPolicies/scm`
  **and** `/ftp` = `allow=false`; publishing creds → Kudu `/api/settings` = `401` while disabled.
- Attacker flip `scm` → `allow=true` (`PUT .../basicPublishingCredentialsPolicies/scm`); after ~30–40 s
  propagation the same creds → `200`, and `POST /api/command {"command":"whoami & hostname"}` returned
  `IIS APPPOOL\htrcfaw16266` + host, `ExitCode 0` = **Entra-independent command exec** (pure HTTP Basic,
  no token / MFA / CA).
- **Eviction latency:** flipping `scm` back to `allow=false` cut Kudu off `200`→`401` within **~12–24 s**.
- **Key persistence nuance (novel vs wiki):** the SCM login carries no Azure identity, so it is a per-site
  static secret unaffected by removing the retriever's RBAC role — real containment is the policy toggle
  (or rotating the creds), NOT de-provisioning the principal. Added a lab-verified WARNING to
  `az-functions-app-privesc.md` (privesc mechanism was already documented — only the persistence/eviction
  angle + the `/api/command` exec example are additive). **Teardown:** `az group delete htrc-scm`.
| 5 | Easy Auth secret theft + auth bypass | `sites/config/write` | DOC-ONLY |
| 6 | Access-restriction removal | `sites/config/write` | DOC-ONLY |
| 7 | Attacker-Relay hybrid connection | `sites/hybridConnectionNamespaces/relays/write` | DOC-ONLY |
| 8 | **RCE via app-settings/env vars** (appCommandLine, Oryx PRE/POST_BUILD_COMMAND, DOTNET_STARTUP_HOOKS, NODE_OPTIONS=--require, JAVA_TOOL_OPTIONS -javaagent, PYTHONPATH+sitecustomize, LD_PRELOAD) | `Microsoft.Web/sites/config/write` | DOC-ONLY |
| 9 | Functions `WEBSITE_RUN_FROM_PACKAGE` remote-URL = full deploy from one setting write | `sites/config/write` | **WORKS — lab-verified 2026-09-24 on Windows Consumption**; the Linux Consumption 503 was inconclusive, not a platform rejection |
| 10 | Functions `hostruntime/*` ARM-proxy → master key | `hostruntime/*` | **REFUTED — lab-verified 2026-09-24**: key routes return 401; host/status recon works, while the separate `sites/host/listkeys/action` is the valid key path |
| 11 | Container Apps external ingress is public by default | none | **DOC-CORRECTED 2026-09-26** — ingress is disabled unless configured and `external` defaults to `false`; only explicitly external apps are public |

Env-var facts baked in: NODE_OPTIONS blocks --eval/-e (use --require <file>); PYTHONSTARTUP is
interactive-only (use PYTHONPATH+sitecustomize); JAVA_OPTS is not a JVM var (use JAVA_TOOL_OPTIONS).

**Lab record (test #9, 2026-09-24 — Windows Consumption remote package):** The original live-fire commit
`cda2c91cd` used a Windows Consumption Function App and an anonymous Node.js HTTP trigger whose
`index.js` called `child_process.execSync`. The ZIP was served through a read SAS URL. Changing only
`WEBSITE_RUN_FROM_PACKAGE` through `Microsoft.Web/sites/config/write`, then restarting the host, made the
Function mount and execute the package: its response included `whoami` as
`iis apppool\...node_24...`, the hostname, and environment output. No storage key, file-share permission,
SCM credential, or publish permission was used. A Linux Consumption attempt returned 503, but its package
and configured runtime were not isolated well enough to contradict Microsoft's documented URL support;
that result is now explicitly inconclusive and queued for retest. The original commit did not retain the
resource identifiers; a 2026-09-26 subscription inventory found no residual research Function App/RG.

**Lab record (test #10, 2026-09-24 — `hostruntime` key-route correction):** The original live-fire commit
`8f828a1ec` called the ARM-proxied runtime routes on a real Function App. `hostruntime/host/read` against
`admin/host/status` returned runtime host metadata, while `_master`, host-key, and function-key routes all
returned HTTP 401 with the platform instruction to use a first-class ARM API. The separate
`Microsoft.Web/sites/host/listkeys/action` call returned `masterKey` and `functionKeys`. This is evidence
for a blocked key route plus a valid first-class key path, not a generic `hostruntime/*` master-key read.
The original commit did not retain the resource identifiers; the later inventory found no residual test
Function App/RG.
