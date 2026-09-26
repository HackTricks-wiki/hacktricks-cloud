# Azure SQL — Tests Done

Wiki: SQL privesc/post-exploitation/persistence pages. **Microsoft.Sql has 0 ARM dataActions**
(data plane is pure T-SQL). Op names verified in `scratchpad/sql_all_writes.txt`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `##MS_LoginManager##`/`##MS_*##` fixed server roles + IMPERSONATE/EXECUTE AS + db_owner escalation | T-SQL | CANT-TEST (no live SQL server / no 1433) |
| 2 | virtualNetworkRules + additive outboundFirewallRules reachability/exfil | `servers/write` | DOC-ONLY |
| 3 | databases createMode Secondary/Copy + failoverGroups continuous exfil (same tenant, no read event) | `databases/write`+`failoverGroups/write` | DOC-ONLY |
| 4 | Disable Advanced Threat Protection (Defender for SQL) | `.../advancedThreatProtectionSettings/write` | DOC-ONLY |
| 5 | Backup/LTR/WORM-immutability destruction (anti-recovery) | those actions | DOC-ONLY (not fired) |
| 6 | Auditing + diagnosticSettings teardown | write/delete | DOC-ONLY |
| 7 | SQL Data Sync attacker member | `syncGroups/write` | DOC-ONLY |
| 8 | `dnsAliases/acquire` alias hijack (persistence) | that action | DOC-ONLY |
| 9 | `encryptionProtector/write` TDE-repoint kill-switch (persistence) | that action | DOC-ONLY |

**Wall:** SQL logical server provisioning blocked in lab + no usable outbound 1433 → no live T-SQL path.
Control-plane ops catalog-confirmed; T-SQL from MS docs.
