# Cloud NAT research log

## 2026-09-29 — Private NAT source-based rules and trusted-range impersonation

### Hypothesis

An attacker who can update a source VPC's existing Private NAT gateway can selectively translate an attacker workload into a `PRIVATE_NAT` range already trusted by an NCC-connected destination. This should cross a source-CIDR authorization boundary without a destination firewall or IAM-policy write. The September 2026 source-based rule extension should allow the change to target only a chosen source range.

### Live matrix

- Built two disposable custom VPCs connected as active linked-VPC spokes to one NCC hub. The source VM was `10.10.1.2`; the destination HTTP fixture was `10.20.1.2:8080`.
- The destination firewall allowed TCP/8080 only from the disposable `172.16.0.0/28` `PRIVATE_NAT` subnet. The source VPC had an active NCC route to `10.20.1.0/24`.
- Negative control: before Private NAT, repeated source requests timed out. This separated routing from authorization: NCC supplied the route, but the destination did not trust `10.10.1.2`.
- A next-hop-only Private NAT rule translated the same requests successfully. The destination application returned source `172.16.0.2`.
- The v1 endpoint rejected a combined source/next-hop expression with the explicit message that source expressions in Private NAT are supported only in beta. The beta endpoint accepted:
  `inIpRange(source.ip, "10.10.1.0/24") && nexthop.hub == "//.../hubs/<hub>"`.
- With that selector, requests continued succeeding as `172.16.0.2`. Changing only the source selector to nonmatching `10.10.2.0/24` made new requests time out again. This confirms selective source matching rather than merely gateway-wide translation.

### Permissions and telemetry observed

- Source-rule writes emitted paired Admin Activity operation records under `beta.compute.routers.patch`; the next-hop-only v1 writes used `v1.compute.routers.patch`.
- The initiating beta record checked exactly `compute.routers.update` on the router and `compute.networks.updatePolicy` on the source VPC. Its request retained the full rule number, CEL match, and `action.sourceNatActiveRanges` URL.
- With NAT logging explicitly enabled, `compute.googleapis.com/nat_flows` on `nat_gateway` recorded original source `10.10.1.2`, translated source `172.16.0.2`, destination `10.20.1.2:8080`, and allocation status `OK`.
- With destination Firewall Rules Logging enabled, `compute.googleapis.com/firewall` on `gce_subnetwork` recorded the allowed request with source `172.16.0.2`; it did not expose the original workload address in that firewall record.

### Boundaries and classification

- Expected Private NAT behavior, not a vulnerability. Publish as bounded Compute/VPC post-exploitation because source CIDRs are frequently treated as a trust boundary.
- Requires an existing or separately creatable Private NAT gateway/range and NCC or supported hybrid route. It does not choose an arbitrary translated IP, grant IAM, defeat TLS/application authentication, override source egress policy, or create unsolicited inbound reachability.
- The destination must already trust the NAT range. Without that configuration error/design choice, the router update does not create authorization by itself.
- Source-based rules use the beta endpoint at the time of testing. Keep `beta.compute.routers.patch` distinct from stable next-hop-only `v1.compute.routers.patch` in detections.

### Cleanup

- Deleted both VMs and boot disks, Cloud Router/NAT, all three firewall rules, both NCC spokes, the hub, three subnets, and both VPCs.
- Removed the test-generated project SSH metadata line and local SSH/startup artifacts while preserving the three pre-existing project SSH entries.
- Verified zero `ht-pnat-*` instances, disks, routers, firewall rules, subnets, networks, hubs, or spokes; no new Compute/NCC service-agent binding remained. Compute and NCC APIs stayed enabled as at baseline.

