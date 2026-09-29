# reCAPTCHA Enterprise post-exploitation — documentation audit

## 2026-09-28 — full page review

This review used current official Google Cloud/Google reCAPTCHA documentation and local `gcloud` help only. No project, key, policy, assessment, identity, API state, or other cloud resource was read or changed.

### Retained techniques

1. **Key and Universal-policy weakening.** `recaptchaenterprise.keys.update` can disable domain, package, or bundle enforcement and soften supported challenge settings. `recaptchaenterprise.policies.update` can weaken a Universal key's domain, endpoint, and challenge policy. Application-side token-property and score checks still bound impact.
2. **IP score override.** `keys.addIpOverride` uses `recaptchaenterprise.keys.update` and returns score `0.9` for valid assessments whose token originated at the allowlisted public IP/CIDR. It does not validate invalid tokens and does not use the request's `event.userIpAddress` value.
3. **Firewall-policy tamper.** Project firewall policies can return an attacker-favorable action, but only an application that requests `firewallPolicyEvaluation`, supplies `requestedUri` for path matching, and enforces the suggested action is affected.
4. **Legacy verifier-secret retrieval.** The method is HTTP `GET` and the permission type is `ADMIN_READ`. Current key documentation says site keys have a legacy secret for third-party integrations; it is not limited to migrated keys. The secret authorizes token verification but cannot mint a valid response token or forge Google's response. The separately documented `SiteVerify` fail-open requires an automatically migrated Classic account, no billing, and prior exhaustion of the organization-wide free allowance; the documentation does not establish that secret possession or invalid-token probes alone can trigger it.
5. **False assessment annotations.** Premium and Enterprise tiers accept annotations used to tune the site-specific model. This is probabilistic feedback poisoning and requires a known assessment resource name; there is no assessment list API.
6. **Related-account reconnaissance.** The Pre-GA, Enterprise-tier group/membership APIs return stable account IDs and their behavioral clusters. Full enumeration needs both group-list and membership-list permissions; a search for a known account uses the membership-list permission.

### Material corrections to the previous page

- Replaced abbreviated/reasoned log names with the exact `google.cloud.recaptchaenterprise.v1.RecaptchaEnterpriseService.*` methods from the current audit catalog.
- Corrected `RetrieveLegacySecretKey` from guessed `DATA_READ` to `ADMIN_READ`, and corrected the request from `POST` to `GET`.
- Corrected `CreateAssessment` from `DATA_READ` to `DATA_WRITE`. Both v1 assessment and annotation Cloud Audit records are deprecated; current visibility is through independently configurable `assessment` and `annotation` platform logs. The official platform-log page does not state the initial toggle state, so the book does not invent one.
- Added the required `--web`, `--android`, and `--ios` selectors to current `gcloud recaptcha keys update` commands and bounded key-type-specific flags.
- Replaced “always passes” IP-override language with the exact valid-assessment score of `0.9` and the actual token-source-IP prerequisite.
- Removed the unsupported claim that a legacy secret forges server-side validation. SiteVerify still requires a fresh single-use response token, and the victim receives Google's response directly.
- Made firewall-policy enforcement conditional on the application evaluating and honoring the returned action rather than describing policy storage as an automatic WAF bypass.
- Updated product gating to the current Essentials/Premium/Enterprise tiers: annotations require Premium or Enterprise; Related accounts requires Enterprise.

### Folded or removed as low-value, misplaced, or unsupported

- A create-only `testingOptions.testingScore` key is not useful without a separate deployment/config change that swaps the victim application to the new key; an actor able to make that application change can remove reCAPTCHA directly. It is not retained as a standalone service post-exploitation primitive.
- `assessments.create` by itself evaluates a caller-supplied event/token. It is ordinary data-plane use, not a read of stored victim assessments; quota burn alone is destructive abuse and is not a retained heading.
- Generic key/metrics/firewall listing belongs in service enumeration. `projectmetadata` speculation was removed because no documented security-relevant post-exploitation outcome was established.
- Delete operations and deny-all testing keys are availability attacks, not high-value post-exploitation techniques for this page.

### Telemetry conclusions

- `UpdateKey`, `UpdatePolicy`, `AddIpOverride`, and firewall-policy create/update/reorder are `ADMIN_WRITE` Admin Activity and always on.
- `RetrieveLegacySecretKey`, `ListIpOverrides`, key/policy/firewall reads, and related-account reads are Data Access and absent by default. The audit catalog explicitly types secret retrieval, IP-override listing, and related-account search as `ADMIN_READ`.
- v1 assessment and annotation platform logs are per-operation toggles. They contain the Assessment response or AnnotateAssessmentRequest, exclude Fraud Prevention PII, and do not cover v1beta1 or SiteVerify.

## 2026-09-28 — independent cross-review

- Rechecked all six retained H3s against the current v1 discovery document, REST resources, audit catalog, product guides, tier matrix, and locally installed Google Cloud CLI 586.0.0 help/source. No cloud resource or project state was read or changed.
- Added the omitted setting-specific gates: challenge preferences apply only to `CHECKBOX`, `INVISIBLE`, and `POLICY_BASED_CHALLENGE` web keys; score-threshold updates require a Premium or Enterprise policy-based challenge key; Policy Engine requires a Premium or Enterprise Universal key, is Preview, and Premium is capped at three rules.
- Corrected the firewall prerequisite boundary: path-based matching also depends on `event.requestedUri`, and returned actions are recommendations the assessment caller must execute. reCAPTCHA does not itself enforce the allow/block/substitute response.
- Tightened the legacy-secret chain. Secret retrieval permits legacy verification of response tokens, but the documented fail-open occurs only after an automatically migrated Classic account without billing has exceeded the organization-wide free assessment allowance. Official documentation does not establish that invalid-token probes consume that allowance, so secret possession alone is not presented as a quota-exhaustion primitive.
- Marked Related Accounts as Pre-GA as well as Enterprise-only. Confirmed that the REST search request accepts `accountId` and `pageSize` in its JSON body, while the list calls accept `pageSize` as a query parameter.
- Reconfirmed exact telemetry: management writes are always-on `ADMIN_WRITE`; legacy-secret retrieval and IP-override listing are optional `ADMIN_READ` Data Access; the audit catalog leaves the two related-account list permission-type cells empty but classifies the methods as Data Access; search is `ADMIN_READ`; deprecated assessment audit methods are not substituted for optional v1 platform logs.
