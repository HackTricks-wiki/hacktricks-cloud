# Dataplex — tested

Dataplex. Enum + privesc pages; the two Metadata Jobs techniques (org-wide EXPORT exfil, FULL-sync
IMPORT deletion) filed on the privesc page. No post-ex/persistence page (by choice — thin surface).

## Standing UNVERIFIED candidate
- `tasks.update` actAs-bypass hypothesis — whether editing an existing Dataplex task's spec runs
  attacker code as the task's service account without holding `iam.serviceAccounts.actAs`. **Not
  verified, omitted per no-garbage.**
