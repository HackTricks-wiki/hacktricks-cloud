# Iap — tested

Identity-Aware Proxy (IAP). Covered: unauth `allUsers`→`iap.httpsResourceAccessor` bypass and durable resource-IAM binding persistence.

## 2026-09-26 — OAuth client secret claim removed; audit claims narrowed
- Google's [programmatic authentication](https://docs.cloud.google.com/iap/docs/authentication-howto) guide requires a Google-issued ID token for an authorized user/service account or a signed service-account JWT. Its [OAuth client sharing](https://docs.cloud.google.com/iap/docs/sharing-oauth-clients) guide explicitly says a leaked client secret affects authentication, **not** authorization, and the caller still needs IAP IAM access. The previous privesc/persistence pages incorrectly treated a client secret alone as an IAP bypass/backdoor. Removed both sections and the standalone ClientAuthConfig privesc page, which also relied on the [retired IAP OAuth Admin API](https://docs.cloud.google.com/iap/docs/deprecations/migrate-oauth-client). This was a source-based correction; no infrastructure used.
- The [IAP audit method table](https://docs.cloud.google.com/iap/docs/audit-log-howto) does not list runtime `accessViaIAP` authorization, but that omission alone does not prove every tunnel or web request emits no Cloud Audit entry with Data Access enabled. Replaced categorical silence claims with an explicit unverified classification and pointed to guest, load-balancer, and app logs. `SetIamPolicy` remains always-on `ADMIN_WRITE`; `UpdateIapSettings` is `DATA_WRITE` off by default. Added four explicit stealth ratings to the retained IAP privesc sections.
- Corrected the persistence tunnel PoC: `gcloud compute instances add-iam-policy-binding` targets the Compute Engine VM policy, while [IAP's access guide](https://docs.cloud.google.com/iap/docs/using-tcp-forwarding) and [resource path reference](https://docs.cloud.google.com/iap/docs/managing-access) use `projects/<NUMBER>/iap_tunnel/zones/<ZONE>/instances/<VM>:setIamPolicy`. The book now shows a read-modify-write against the IAP resource itself. This was source-grounded; no VM was created.

## Standing items
- Beta egress `iap.webServiceVersions.egressViaIAP` audit class unconfirmed.
- `serviceusage.contentsecuritypolicy.*` / `groups.*` / `effectivemcppolicy.get` have no verified
  offensive framing yet.
