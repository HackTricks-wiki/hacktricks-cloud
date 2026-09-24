# AWS audit — status

Last updated: 2026-09-24

## Completion state per axis

| Axis | State | Notes |
|---|---|---|
| Privesc (existing services) | ✅ complete | impact + "Logs generated" retrofit done across the 28-page privesc tail |
| Post-exploitation (existing) | ✅ complete | impact + logs retrofit done across the 17-page post-ex tail |
| Persistence (existing) | ✅ complete | + Stealth rating on every persistence technique |
| Privesc/post/persistence (net-new services) | ✅ saturated | 34 net-new pages/techniques; phase-2 zero-presence services swept |
| Unauth / recon (all 433) | ✅ complete | 7 new pages + 7 cross-account resource-policy matrix rows; 8-slice manual pass |
| Cross-account resource-policy matrix | ✅ complete | all 75 policy-setters across 433 enumerated; 65 matrix rows |
| autonomous_research folder | 🟡 in progress | this scaffold; per-service checklists being seeded |

**34 net-new pages/techniques + 27 format-fixed** cumulative. HEAD == origin `6f165c07e`.
PR #413 body updated through the full unauth sweep.

## The 7 convergent lenses

privesc-PassRole · unauth-authtype · recon-output-shape · persistence · hijack-no-PassRole ·
per-service-ledger (`master_ledger.csv`) · 8-slice manual review. All converge on "no further
clean net-new gap that clears the no-garbage bar." Remaining items are reasoned exclusions
(niche/preview/deprecated/cost-blocked) — see each `<service>/tested.md` and `checklist.md`.

## Standing irreversible residue (do NOT re-flag as a mistake)

- `ht-audit-objlock-1790090581` — S3 bucket, one 12-byte object `auto.txt` under COMPLIANCE
  retain-until **2126-08-29**. Undeletable by any principal incl. account root & AWS Support, by
  design. ~$0 cost. Verified empirically. Leave it.
- 2 customer KMS CMKs (`1bb73ce3…`, `acdd6d73…`) in PendingDeletion → self-delete 2026-09-29.
  **Reuse these for KMS tests** instead of creating new CMKs.

Everything else removable has been removed (residue sweep cont.53, 2026-09-24).

## Known content gaps still worth a page (tracked as per-service checklists)

- ElastiCache — has persistence page, still **no enum/privesc/post** pages.
- MemoryDB — persistence only; no privesc/post.
- Glue — no dedicated `aws-services/` enum page.
- `aws-vpn-post-exploitation` — empty stub.
- SSO / Identity Center — persistence angle not yet a page.
- Redshift — privesc+post exist; no persistence/enum-deepen.

## Open-idea backlog lives per service

See `<service>/checklist.md`. When an idea is tested it moves to `<service>/tested.md` with the
result, and — if it works and clears the no-garbage bar — into the public book.
