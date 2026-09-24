# Network Security — tested

Network Security / Cloud NGFW / Cloud IDS / Service Extensions.

## Promoted-after-trying (not merely doc-inferred)
- TLS Inspection Policy MITM (`tlsInspectionPolicies.create/.update+.use` + `gatewaySecurityPolicies.
  update/.use`) promoted to a documented technique.
- Cloud NGFW Enterprise L7-IPS evasion: `networksecurity.securityProfiles.update` flips
  threat-prevention→ALLOW, carried by the common `roles/compute.networkAdmin`;
  `firewallEndpointAssociations.delete` detaches inspection; `dnsThreatDetectors.delete/update` blinds
  DNS-threat detection.
- Service Extensions MITM: abusable perms live under `networkservices.*`, NOT `serviceextensions.*`.
