# GCP audit — open frontier (next-iteration candidates)

State (2026-09-25): the authenticated technique surface is at deep saturation. Six independent
diff/scan axes run this engagement all came back exhausted beyond the 3 gaps shipped in batch 4:
service-prefix diff, individual-write-perm diff, resource-type-token diff, setIamPolicy/use/actAs
diff, credential/token-mint diff, and a fresh-catalog delta (only 21 perms added since the
session-8 dump, none attack-relevant). Remaining real gaps appear as **newly-GA/preview
sub-resources within already-documented services** — a slow trickle, not a backlog.

## Open, genuinely-uncovered leads deferred for lack of testable infra (verify when feasible)
- [ ] **googleTagGatewayPolicies end-to-end** — SHIPPED from API surface (batch 4). When the resource
      reaches GA + gcloud support, live-verify the first-party-JS injection by standing up an external
      Application LB + backend + attaching a policy in the lab, and confirm an attacker GTM tagId's
      custom-HTML JS actually executes first-party. Upgrade the page's caveat if verified.
- [ ] **iam.oauthClients token-exchange** — SHIPPED persistence (attacker half live-verified). If a
      workforce identity pool + external IdP can be stood up (needs org access), live-verify the
      refresh-token capture end-to-end and quantify the phishing/consent step.

## Monitoring cadence (the productive vein)
- [ ] Periodically re-pull `gcloud iam list-testable-permissions //cloudresourcemanager.googleapis.com/projects/<lab>`
      (needs `gcloud config set billing/quota_project <lab>`), diff vs the prior dump, and triage any
      NEW service prefixes / resource-type tokens for attack primitives. Current baseline dump: 13,698 perms.
- [ ] Watch newly-GA GCP features (release notes) for identity/traffic/exec/exfil surfaces; those are
      where the next real gaps will be (this iteration's 3 were all GA-2024/preview resources).

## Assessed and intentionally NOT authored (no-garbage bar)
- compute.instantSnapshots — same disk-exfil family; annotated as a NOTE, not a technique.
- compute.regionSslPolicies.setIamPolicy, dataplex.entryLinkTypes.* — generic self-grant / catalog
  metadata; no distinct primitive.
- fpnv.phoneNumberTokens.* — telco/payments test tokens, not a GCP-access primitive.
- KMS kajPolicyConfigs, GKE Backup channels, Storage Insights, Developer Connect, NSI
  mirroring/intercept deployment groups — all covered-concept or documented elsewhere.
