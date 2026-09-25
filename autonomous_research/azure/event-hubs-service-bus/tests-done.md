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
| 6 | **Self-minted SAS authorization-rule persistence + two-key eviction gap** | `namespaces/authorizationRules/write`+`listKeys/action` | **WORKS — lab-verified 2026-09-25 (Service Bus Standard)** |

**Lab record (test, 2026-09-25 — self-minted SAS persistence + two-key gap):** RG `htrc-sbsas`, Service Bus
Standard namespace `htrcsb6964`, queue `htqueue`. Created a rogue namespace `authorizationRule` `htrule` with
`Send Listen`; `keys list` returned primary+secondary (44 chars each). Minted SAS tokens locally with a small
python HMAC helper (`StringToSign = urlencode(resourceUri)+"\n"+expiry`, `sig=base64(HMAC-SHA256(key,STS))`,
header `Authorization: SharedAccessSignature sr=&sig=&se=&skn=htrule`) — **no Azure token** in any request.
Results (curl to `POST https://<ns>.servicebus.windows.net/htqueue/messages`):
- Primary-signed SAS → `201`; secondary-signed SAS → `201` (both send).
- **Two-key gap:** regenerate ONLY `--key PrimaryKey` → primary-signed token `→401` (<6 s) but secondary-signed
  token **still `201`**. Then regenerate `--key SecondaryKey` → secondary-signed token `→401`. So rotating one
  key does NOT evict a token signed with the other; you must rotate BOTH.
- **Rule deletion:** minted a fresh token from current keys (`201` control), deleted the rule → `→401` within
  ~6 s. Alternative eviction lever.
- The SAS carries no Azure identity, so removing the creator's RBAC does nothing to an outstanding token.
Applies identically to Event Hubs (`Microsoft.EventHub/namespaces/authorizationRules/*`). Wiki: added a new
"Self-minted SAS authorization rule" section with the two-key eviction matrix to `az-servicebus-persistence.md`.
**Teardown:** `az group delete htrc-sbsas`.

**DOC-ONLY / not fired:** Geo-DR failover/break (irreversible primitive — hygiene caution, NOT fired);
CMK repoint ransom (Premium/dedicated cost-gated); Geo-DR alias.

**Teardown:** `htrc-rg5` (EH namespace + storage) deleted; `htrc-sbsas` deleted. No residue.
