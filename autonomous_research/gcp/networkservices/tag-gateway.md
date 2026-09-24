# networkservices.googleTagGatewayPolicies — first-party JS injection — SHIPPED

## Result: SHIPPED (post-exploitation / persistence; on gcp-networkservices-privesc.md)
Found via resource-type ground-truth diff: `googleTagGatewayPolicies` had ZERO wiki mention
(no "tag gateway"/"tag manager"/"server-side tag" anywhere).

## Mechanism (from v1alpha1 REST discovery)
GoogleTagGatewayPolicy.perDomainConfig[] fields: domain, enableGtg, measurementPath,
tagId (GT-/G-/AW- Google Tag/GTM container), performTagInitialization (bool), logSampleRate.
Google Tag Gateway = "first-party mode": the external Application LB serves the Google-tag
bootstrap script + proxies measurement requests through the site's own domain.

## Attack
Attacker with googleTagGatewayPolicies.create/update (+ attach to victim Application LB) sets
tagId to an attacker-controlled GTM container + performTagInitialization=true => first-party
script bootstraps the attacker container; GTM custom-HTML tags run arbitrary JS on every visitor.
Bypasses CSP trusting 'self'/Google tag domains; invisible to app code + app WAF; standing backdoor.

## Verification / honesty
- Perm confirmed in roles/networkservices.editor + admin (gcloud iam roles describe).
- Resource is alpha REST-only (networkservices v1alpha1; no gcloud group). NOT live-verified
  end-to-end (needs an external App LB + domain + real tag serving; alpha, not gcloud-creatable).
  Arbitrary-JS step relies on standard GTM custom-tag behavior. Documented from API surface with
  explicit alpha/preview + not-live-verified caveats (same honesty bar as authzExtensions/AR export).

## Bar
Genuine, novel, high-impact, completely undocumented client-side/supply-chain primitive; the
permission is in the production IAM taxonomy. Ships with honest preview caveat.
