# Event Hubs / Service Bus — Tests Done

Wiki: `az-event-hubs-privesc.md`, `az-event-hubs-post-exploitation.md`, `az-event-hubs-persistence.md`,
plus Service Bus pages.

**LAB-VERIFIED on a Standard Event Hubs namespace:**
| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | Capture repoint → attacker storage container (Avro), then read captured Avro | `namespaces/eventhubs/write` + storage write | **WORKS** |
| 2 | Covert consumer-group create (persistence) | `.../consumergroups/write` | **WORKS** |
| 3 | Retention purge → 1 day (DoS/anti-forensics) | `namespaces/eventhubs/write` | **WORKS** |
| 4 | `disableLocalAuth` true/false toggle | `namespaces/write` | **WORKS** |
| 5 | `networkRuleSets` flip (exposure/lockout) | `namespaces/networkRuleSets/write` | **WORKS** |

**DOC-ONLY / not fired:** Geo-DR failover/break (irreversible primitive — hygiene caution, NOT fired);
CMK repoint ransom (Premium/dedicated cost-gated); self-minted SAS rule persistence; Geo-DR alias.

**Teardown:** `htrc-rg5` (EH namespace + storage) deleted. No residue.
