# Autonomous Research — GCP

Persistent research log for the HackTricks Cloud GCP technique audit (PR #414, branch
`gcp-techniques-audit-2026-09`). This folder is the browsable, per-service record the `/goal`
asks for so that **future agents know what has already been tested, what worked, and what is
still open** — without re-reading the whole git history or the memory prose.

> This is an **internal research-tracking artifact**, not wiki content. Confirmed, useful
> techniques live in the public book under `src/pentesting-cloud/gcp-security/`. This folder
> only records *process*: what was tried, the result, and the still-open idea backlog.

## How this folder is organized

```
autonomous_research/gcp/
  README.md              <- this file (methodology + hygiene rules)
  STATUS.md              <- per-axis completion state, standing residue, open gaps
  _deferred-and-excluded.md  <- services verified to NOT need a page/technique, with reasons
  <service>/
    tested.md            <- techniques attempted on the service + result (worked / didn't / why)
    checklist.md         <- OPEN ideas still to test (removed from here once tested -> tested.md)
```

A service only gets a subfolder when there is something worth recording beyond "fully covered
in the book" — i.e. it has an **open idea backlog** or a **non-obvious result** (a live-fire
confirmation, a negative result, or an environment block) worth preserving so no future agent
wastes time re-deriving it.

## The four axes tracked per service

1. **Privilege escalation** — a permission/primitive lets a principal reach a higher-privileged identity or resource. Wiki page carries **Minimum permissions + Potential Impact + expandable "Logs generated"**.
2. **Post-exploitation** — abuse with already-held access (data exfil, lateral movement, DoS, anti-forensics). Same format; **Potential Impact + Logs generated**.
3. **Persistence** — durable backdoor access surviving cleanup. Same format; **Logs generated** (and a stealth note where relevant).
4. **Unauthenticated / recon** — what an attacker with **no GCP credentials** (or only a throwaway `allAuthenticatedUsers` Google account) can discover or abuse per service. Lighter page format (no min-perms/logs table — no principal): discover the public resource + abuse it.

## Qualifying rules (the "no garbage" bar)

- **Unauth page** — a GCP service needs a dedicated unauth page **iff** it has resource-level IAM
  that accepts `allUsers`/`allAuthenticatedUsers` **AND** an outsider-reachable data plane
  (bare-anonymous HTTP like Storage/Run/Functions/API-Gateway, **or** an OAuth-token-from-throwaway-account
  plane like BigQuery/Pub-Sub/Healthcare/Secret Manager/Bigtable/Cloud Tasks where the API validates
  the token *before* IAM so `allUsers`≈`allAuthenticatedUsers` but no target-project access is needed).
- **Env-var → RCE** — only a *meaningful* primitive where the env var reaches an interpreter startup
  hook (NODE_OPTIONS=--require, PYTHONPATH+sitecustomize, JAVA_TOOL_OPTIONS=-javaagent, …). If the
  service already lets you set the command/image/source directly, an env-var row is redundant garbage.
- Only report techniques that are **real, useful attacks** — verified live, or high-confidence from
  docs when live testing is blocked by the cost/permission exceptions below. Never manufacture pages.

## Test hygiene (binding rules for anyone continuing this loop)

- **Tear down everything you launch.** Never leave test infra. Confirm teardown after every test.
- **Minimum permissions.** Test each technique with the least privilege that confirms it; record
  those perms in the wiki technique. Verify a cited gating permission exists in a real predefined
  role via `gcloud iam roles describe roles/<name>` before shipping.
- **Never live-fire irreversible setters casually.** No blind `Create*`/`Update`/`Patch`/`setIamPolicy`/`delete`
  where the effect is destructive or hard to reverse — schema/role confirmation is enough for those.
- **Cost/time exception.** Skip live testing only if a technique costs >$5/30min, cannot be deleted
  until X time passes, or needs privileges you don't have (then document from docs as high-probability).
- **0-day boundary.** A technique that escapes client-provided infra into Google's **own backend**
  (hypervisor/host escape, cross-tenant, Google-operated services) is a 0-day → **private local report
  for the Google VRP, NOT the public wiki.** Nearly all techniques stay in client infra = normal wiki content.

## Lab account

Project **`gcp-labs-eqd4ny8d`**; the configured service account has `roles/owner` directly on the
project (via local `gcloud`). No org-level or Cloud Identity / Workspace directory-write access, so
Google-Groups / org-policy / directory techniques are documented from docs + role confirmation, not
lab-fired. Persistent lab fixtures already in the project (do NOT delete as if they were test residue):
`appengine-lab-1-*`, `kms-lab-1/2/3-*` keyrings, `pwn-workflow`, `cloudfunction-lab-1/2/3` sources.
