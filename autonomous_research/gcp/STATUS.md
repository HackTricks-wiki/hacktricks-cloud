# GCP audit — status

Last updated: 2026-09-24

## Completion state per axis

| Axis | State | Notes |
|---|---|---|
| Privesc (existing services) | ✅ complete | Minimum permissions + Potential Impact + "Logs generated" expandable on all 75 privesc pages |
| Post-exploitation (existing) | ✅ complete | Impact + Logs generated on all real post-ex pages (README index exempt) |
| Persistence (existing) | ✅ complete | Logs generated on all real persistence pages (README index exempt) |
| Privesc/post/persistence (net-new services) | ✅ saturated | Multi-phase ground-truth diff of the GCP API surface vs wiki; genuine gaps shipped (Cloud Build staging-bucket poisoning, NetApp ONTAP, Public CA EAB, Discovery Engine ACL, Config Delivery, Integration Connectors, App Engine exportAppImage, SSM sshkeys.createAny, + 6 permission-level) |
| Unauth / recon (all services) | ✅ complete | 13 new per-service pages (baseline 11 → 24); every non-qualifying service verified-excluded via the qualifying rule (`_deferred-and-excluded.md`) |
| Env-var → RCE | ✅ complete | 10 qualifying execution services documented in `environment-variable-injection.md`; all others excluded with reasons |
| `autonomous_research/gcp/` folder | 🟡 in progress | this scaffold; per-service `tested.md`/`checklist.md` being seeded from the audit history |

Page counts (branch `gcp-techniques-audit-2026-09`): **75 privesc · 75 post-ex · 55 persistence ·
25 unauth · 89 service-enum**.

## Standing residue / teardown

- **No standing test residue** as of 2026-09-24. The BigQuery test dataset `ht_bq_ds` (copy/restore
  technique test, created 2026-09-22) and 2 orphaned Gen2 Cloud Functions upload zips were deleted
  and verified gone. All prior-phase test RGs/resources torn down.
- **Persistent lab FIXTURES — do NOT delete as residue** (maintainer's pre-built lab targets,
  created months before this audit): `appengine-lab-1-*` (App Engine app + SA + bucket, 2025/2026-08),
  `kms-lab-1/2/3-*` keyrings incl. `-attacker`/`-victim` (2026-04; KMS keyrings are non-deletable by
  design anyway), `pwn-workflow` (Workflows, 2026-06), `cloudfunction-lab-1/2/3` sources in the
  platform `gcf-sources-*` staging bucket (has a `DO_NOT_DELETE_THE_BUCKET.md` marker).

## Method (how completeness was argued)

- **Ground-truth API diff** — botocore-equivalent GCP API models / `gcloud` service surface diffed
  against the wiki corpus to find services/permissions with no coverage (see
  `gcp-wiki-gap-analysis-method` memory).
- **Technique fan-out** — three converging hunters over the authenticated surface (IAM/credentials,
  compute/GKE, storage/serverless/build/data) → one gap (Cloud Build staging bucket), shipped.
- **Unauth sweep** — 5 hunters applying the qualifying rule across all services.
- **Env-var RCE closure** — full execution-service roster, 10 qualifying + reasoned exclusions.
- **Live-fire** where the lab allows (owner on `gcp-labs-eqd4ny8d`); doc-grounded where blocked by
  the cost/permission/org-access exceptions.

## Known open items (tracked as per-service checklists)

Seeded into `<service>/checklist.md`. The eternal loop: when a checklist item is tested it moves to
that service's `tested.md` with the result (and, if it works and is non-duplicate, to the wiki);
when no checklist items remain, generate more non-duplicate candidate ideas.

## Loop iteration log

### 2026-09-24 — batch 1 (initial seeded backlog worked through)
- **Dataplex `tasks.update` actAs-bypass** — live-tested, **REJECTED**: update re-validates
  `iam.serviceAccounts.actAs` on the bound SA for any field, like create. No privesc.
- **Pub/Sub GCS import-topic injection** — live-tested, **SHIPPED**: standing message-injection /
  persistence via `topics.create`/`update` ingestion source (attacker bucket → all subscribers).
- **Artifact Registry `exportArtifact`** — API-verified, **SHIPPED**: reader-level server-side exfil
  to arbitrary GCS bucket.
- **Closed as verified duplicates (already documented, no ship):** ACM `replaceAll` teardown,
  SCC scanner/mute-config evasion, IAP tunnel egress, Secret Manager managed-rotation misuse,
  Cloud Build gen2 `repositories.create` (execution still gated by triggers+actAs).
- **Deferred (verification-only):** Org Policy v2 CreatePolicy/UpdatePolicy audit-class check.
- Backlog empty → generating new candidate batch (WIF federation, Storage Transfer confused-deputy,
  BQ Data Transfer scheduled-query persistence, Cloud Asset exportAssets, Backup&DR, Datastream).
