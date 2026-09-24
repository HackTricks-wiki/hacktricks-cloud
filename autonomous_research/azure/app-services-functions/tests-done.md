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
| 5 | Easy Auth secret theft + auth bypass | `sites/config/write` | DOC-ONLY |
| 6 | Access-restriction removal | `sites/config/write` | DOC-ONLY |
| 7 | Attacker-Relay hybrid connection | `sites/hybridConnectionNamespaces/relays/write` | DOC-ONLY |
| 8 | **RCE via app-settings/env vars** (appCommandLine, Oryx PRE/POST_BUILD_COMMAND, DOTNET_STARTUP_HOOKS, NODE_OPTIONS=--require, JAVA_TOOL_OPTIONS -javaagent, PYTHONPATH+sitecustomize, LD_PRELOAD) | `Microsoft.Web/sites/config/write` | DOC-ONLY |
| 9 | Functions `WEBSITE_RUN_FROM_PACKAGE` remote-URL = full deploy from one setting write | `sites/config/write` | DOC-ONLY |
| 10 | Functions `hostruntime/*` ARM-proxy → `host/_master/read` master key regardless of backend | `hostruntime/*` | DOC-ONLY |
| 11 | Container Apps default-public ingress + revision-suffix recon (unauth) | none | DOC-ONLY (folded into unauth page) |

Env-var facts baked in: NODE_OPTIONS blocks --eval/-e (use --require <file>); PYTHONSTARTUP is
interactive-only (use PYTHONPATH+sitecustomize); JAVA_OPTS is not a JVM var (use JAVA_TOOL_OPTIONS).
