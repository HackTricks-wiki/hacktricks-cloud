# Dataplex — tested

Dataplex. Enum + privesc pages; the two Metadata Jobs techniques (org-wide EXPORT exfil, FULL-sync
IMPORT deletion) filed on the privesc page. No post-ex/persistence page (by choice — thin surface).

## `tasks.update` actAs-bypass hypothesis — TESTED, REJECTED (no privesc)

Hypothesis: a principal holding `dataplex.tasks.update` but **not** `iam.serviceAccounts.actAs` on a
task's bound execution SA could edit an existing Dataplex task's spec (script / Spark args / lifetime)
to run attacker-controlled code as that higher-privileged SA — a confused-deputy privesc.

Live test (lab `gcp-labs-eqd4ny8d`, all infra since torn down):
- Created lake `htrc-dplake`; created task `htrc-dp-task` (ON_DEMAND, no run = no cost) bound to a
  target SA, as the owner identity (which holds actAs).
- Created a custom role with `dataplex.tasks.{get,list,update}` + dataplex read perms and **no**
  `iam.serviceAccounts.actAs`; granted it to an attacker SA; authed directly as that SA (key).
- Attacker could `tasks.describe` (read the bound SA), then attempted `tasks.update`:
  - rewrite `--spark-python-script-file` → **`INVALID_ARGUMENT: User does not have permission to act
    as '<target SA>'`**
  - change only a benign field (`--execution-args`, `--max-job-execution-lifetime`) → **same actAs
    rejection**.

**Conclusion:** `dataplex.tasks.update` re-validates `iam.serviceAccounts.actAs` on the task's bound
service account for *any* field change, exactly like `tasks.create`. No confused-deputy, no actAs
bypass. **Not a real privesc — nothing shipped to the wiki.** Do not re-test unless the update
authorization model changes.
