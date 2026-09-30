# Data Factory / Synapse — Tests Done

Wiki: `az-data-factory-privesc.md`, `az-synapse-analytics-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | ADF sandbox **debug** RCE-as-MSI | `factories/.../debug` | DOC-ONLY |
| 2 | ADF `getDataPlaneAccess`, dataflow debug, IR regenerate/getconnectioninfo/link | those actions | DOC-ONLY |
| 3 | ADF `getGitHubAccessToken` | that action | **UNVERIFIED** — never fired |
| 4 | Synapse firewall open | `workspaces/firewallRules/write` | DOC-ONLY |
| 5 | Synapse rogue Self-Hosted IR | IR write | DOC-ONLY |
| 6 | Synapse `bigDataPools` Spark RCE | pool write | **UNVERIFIED** |
| 7 | Synapse `managedIdentitySqlControlSettings`, workspace Git, SQL audit/ATP disable | those actions | DOC-ONLY |

**0day boundary:** cross-tenant IR RCE = 0day → private report, NOT wiki (`azure-0day-boundary-rule`).
