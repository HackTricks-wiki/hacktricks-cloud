# Data Explorer (Kusto/ADX) — Tests Done

Wiki: `az-data-explorer-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `AddPrincipals` / `.add admins` data-plane self-grant | cluster admin data-plane | DOC-ONLY (separate plane, blind spot) |
| 2 | python/R sandbox escape | data-plane | **UNVERIFIED** |
| 3 | `AddCalloutPolicies` SSRF | admin | DOC-ONLY |
| 4 | Continuous-export exfil | admin | DOC-ONLY |
| 5 | Cross-cluster follower | admin | DOC-ONLY |
| 6 | Data-connection hijack | admin | DOC-ONLY |
