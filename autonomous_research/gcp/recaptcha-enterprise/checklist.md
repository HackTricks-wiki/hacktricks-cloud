# reCAPTCHA Enterprise post-exploitation research checklist

## Completed documentation and local-source checks — 2026-09-28

- [x] Classify every original heading as useful post-exploitation, configuration evasion, recon,
  availability, or unsupported.
- [x] Verify key patch, IP override, firewall-policy, Universal-policy, assessment annotation, legacy
  secret, and related-account minimum permissions against current REST/IAM documentation.
- [x] Verify current `gcloud recaptcha keys update`, IP-override, and firewall-policy flags locally.
- [x] Bound domain/package/bundle relaxation by independent backend token-property validation.
- [x] Bound IP overrides to valid assessments, the real token source IP, and score `0.9`.
- [x] Bound firewall-policy effects to integrations that request evaluation and enforce the result.
- [x] Correct legacy-secret HTTP semantics, applicability, and non-forgery impact.
- [x] Verify current Essentials/Premium/Enterprise feature gates.
- [x] Verify exact audit method names, permission types, deprecated assessment audit logs, platform-log
  coverage, and default visibility without inventing an undocumented platform-log default.
- [x] Add minimum prerequisites, bounded Potential Impact, categorical Stealth, and expandable exact
  log tables to every retained H3.
- [x] Validate references, shell snippets, Markdown fences/details, and scoped diff.
- [x] Independently recheck key-type and tier gates, IP-override propagation/source behavior,
  firewall `requestedUri` matching and caller enforcement, legacy fail-open boundaries, annotation
  model claims, Related Accounts Pre-GA status/request schemas, and exact audit/platform-log defaults.

## Future safe validation leads

- [ ] In a dedicated authorized test project, capture the precise request/response fields retained in
  Admin Activity for key, policy, IP-override, and firewall-policy changes; document observations as
  dated evidence rather than API guarantees.
- [ ] Determine the initial state of the assessment and annotation platform-log toggles for a newly
  provisioned project. Current official documentation describes enable/disable controls but not the
  default.
- [ ] With Premium test entitlement, measure whether a bounded set of contradictory annotations has
  any observable short-term effect; do not state a deterministic poisoning threshold without data.
- [ ] With Enterprise test entitlement and synthetic account IDs only, capture the exact Cloud Audit
  entries for group listing, membership listing, and membership search.
- [ ] Verify which current web-key creation/migration variants return a legacy secret and how
  unauthorized SiteVerify usage appears in key metrics, without exhausting paid quota.

## Do not restore without stronger evidence

- [ ] Do not describe a legacy verifier secret as the ability to mint tokens or forge Google's
  response to the victim backend.
- [ ] Do not describe legacy-secret retrieval alone, or undocumented invalid-token probes, as a proven
  way to exhaust the organization-wide assessment allowance and trigger `SiteVerify` fail-open.
- [ ] Do not call an IP override an unconditional pass; it returns `0.9` only for valid assessments.
- [ ] Do not call stored firewall policies an automatic WAF bypass unless the target integration
  requests policy evaluation and enforces the suggested action.
- [ ] Do not claim assessment/annotation Cloud Audit Data Access is the current detection source; those
  records are deprecated in favor of optional v1 platform logs.
- [ ] Do not restore create-only testing keys as a standalone technique without a distinct,
  service-level path that makes a victim application adopt the new key.
