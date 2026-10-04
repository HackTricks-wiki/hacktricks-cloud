# Cloud NAT research checklist

## Completed

- [x] Separate NCC route availability from destination source-range authorization with a negative
      control.
- [x] Confirm a next-hop-only Private NAT rule makes the destination observe the trusted NAT range.
- [x] Confirm beta source-based matching accepts `source.ip && nexthop.hub` and targets only the
      matching workload range.
- [x] Capture exact router-patch methods, permissions, request fields, NAT flow fields, and
      destination firewall attribution.
- [x] Bound the result against arbitrary spoofing, unsolicited inbound access, IAM/application auth
      bypass, egress-policy bypass, and absent destination trust.
- [x] Delete the entire fixture and independently verify cloud, IAM-metadata, service-agent, and
      local-artifact cleanup.

## Follow-up ideas

- [ ] Exercise `nexthop.is_hybrid` in an existing disposable hybrid fixture and compare rule,
      translation, and destination attribution with the NCC hub path. Do not create a billed tunnel
      solely for this check.
- [ ] Test overlapping source rules and rule-number ordering with two disposable NAT ranges; look
      for stale translation or configuration/data-plane disagreement after rapid updates. Keep any
      unexpected mismatch private-first.
- [ ] Compare exact source selectors, IPv4/IPv6 validation, malformed CEL, API-version parity, and
      propagation timing without sending traffic outside owned synthetic networks.
- [ ] Measure the smallest predefined/custom role and whether conditions can constrain router and
      VPC writes independently; retain the observed permission pair as the raw API minimum.
- [ ] Test application-layer IP allowlists and proxy/header attribution only against an owned
      fixture. Do not generalize firewall behavior to identity-aware applications.
