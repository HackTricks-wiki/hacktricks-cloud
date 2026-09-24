# Autonomous Research — AWS

Persistent research log for the HackTricks Cloud AWS technique audit (PR #413, branch
`research/aws-technique-audit`). This folder is the browsable, per-service record the `/goal`
asks for so that **future agents know what has already been tested, what worked, and what is
still open** — without re-reading the whole git history or the memory prose.

> This is an **internal research-tracking artifact**, not wiki content. Confirmed, useful
> techniques live in the public book under `src/pentesting-cloud/aws-security/`. This folder
> only records *process*: what was tried, the result, and the still-open idea backlog.

## How this folder is organized

```
autonomous_research/aws/
  README.md            <- this file (methodology + status)
  STATUS.md            <- one-line-per-axis completion state + the 7 lenses
  <service>/
    tested.md          <- techniques attempted on the service + result (worked / didn't / why)
    checklist.md       <- OPEN ideas still to test (removed from here once tested -> tested.md)
```

A service only gets a subfolder when there is something worth recording beyond "fully covered
in the book" — i.e. it has an **open idea backlog** or a **non-obvious negative result** worth
preserving so no future agent wastes time re-testing it.

## Methodology (7 convergent lenses over all 433 botocore services)

Every AWS service in the botocore model (433) was assessed for missing privesc / post-exploit /
persistence / unauth-recon techniques through seven independent lenses. Convergence of all seven
on "no further clean gap" is the completeness argument:

1. **privesc-PassRole** — every op whose input takes a role ARN + a compute/data sink (confused-deputy exec/exfil as the passed role).
2. **unauth auth-type** — services whose data plane is non-SigV4 (None / bearer / api-key / IP-policy) → anonymous or leaked-token access.
3. **recon output-shape** — ops whose *output* returns a genuine secret VALUE (not id/arn/token-suffix).
4. **persistence** — durable non-IAM credential/ACL/key primitives (RBAC users, API keys, role aliases, rotation freeze…).
5. **hijack-existing-compute-no-PassRole** — inject code into compute that *already* has a role (UpdateFunctionCode, lifecycle configs, task-defs…).
6. **per-service ledger** — `master_ledger.csv`: one explicit signal verdict per service for all 433.
7. **8-slice manual review** — human-style per-service reading against 6 recon/unauth categories (found the non-IAM auth-plane gaps the programmatic lenses structurally could not see).

Full evidence trail: the memory file `aws-technique-audit-progress.md` (checkpoints cont.1–cont.53)
and the session scratchpad artifacts `LEDGER.csv` / `PROBE_LEDGER.tsv` / `TRACKER.md`.

## Test hygiene (binding rules for anyone continuing this loop)

- **Tear down everything you launch.** Never leave test infra. Confirm teardown after every test.
- **Minimum permissions.** Test each technique with the least privileges that confirm it; record those perms in the wiki technique.
- **No garbage.** Only report techniques that are real, useful attacks — verified OR high-confidence
  from docs when live testing is blocked by the cost/permission exceptions. Never manufacture pages.
- **Cost/time exception.** Skip live testing only if a technique costs >$5/30min, cannot be deleted
  until X time passes, or needs privileges you don't have (then document from docs as high-probability).
- **Irreversible-primitive caution.** For Object-Lock / retention / compliance tests use the **minimum
  1-day** retention, never a long/auto retain-until (see the standing residue note in STATUS.md).
- **0-day boundary.** A technique that lands in real AWS *underlying* infra (not client-provided infra)
  is a 0-day → private local report to AWS, **not** the public wiki.

## Lab account

Account `228478051196`, local profile **`ht-admin`** (plain `hacktricks-training` resolves to the
WRONG account `418720621023`). SCP-region-locked to **us-east-1 + eu-west-1** (other regions
explicit-deny). Org ID for `aws:PrincipalOrgID` conditions: `o-bsfj09ozhf`.
