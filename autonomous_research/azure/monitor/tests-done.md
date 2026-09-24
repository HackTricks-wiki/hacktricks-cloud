# Monitor — Tests Done

Wiki: `az-monitor-post-exploitation.md` (+ Log Analytics pages), unauth `az-monitor-alert-phishing`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | App Insights instrumentation key / live-token abuse | data-plane | **WORKS** (5 primitives lab-verified, commit 03e90018b) |
| 2 | Action-group callback abuse | `actionGroups/write` | **WORKS** |
| 3 | Alert linked-auth abuse | alert write | **WORKS** |
| 4 | `dataCollectionRules/write` AMA file exfil | that action | DOC-ONLY |
| 5 | `dataCollectionRules/data/write` forge logs | that action | DOC-ONLY |
| 6 | `autoscale`/`logProfiles` teardown / purge notes | those actions | DOC-ONLY |

**Teardown:** App Insights test resources deleted. No residue.
