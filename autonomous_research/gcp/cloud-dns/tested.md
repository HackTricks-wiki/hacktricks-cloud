# Cloud Dns — tested

Cloud DNS. 11 post-ex techniques; 2 min-perm refinements verified live.

## Key technique
- Cross-tenant zone takeover via dangling nameserver delegation: create zones in the attacker project
  until assigned the victim's shared `ns-cloud-{a-d}{1-4}.googledomains.com` NS set — zero victim
  perms, nothing in victim logs. NS-record subtree delegation one-liner documented.
- Unauth axis: dangling-record subdomain takeover (GCS bucket re-claim) shipped.
