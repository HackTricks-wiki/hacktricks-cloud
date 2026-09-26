# Iap — open ideas

Open ideas — IAP.

- [ ] Confirm runtime tunnel/web audit behavior with Data Access on a disposable IAP-protected target; capture the actual `protoPayload.methodName` if present and compare guest/load-balancer/application request logs. The published method table omits runtime authorization, which is insufficient to claim that it is never logged.

- (none open) — IAP TCP-forwarding as a pivot/egress channel (`iap.tunnelInstances.accessViaIAP`,
  `gcloud compute start-iap-tunnel`, `35.235.240.0/20`) is ALREADY documented in `gcp-iap-enum.md`.
  The only delta was explicit "egress-channel" wording, which is a phrasing nuance, not a new
  technique → no wiki change (no-garbage). `egressViaIAP` beta had no demonstrable distinct attack.
