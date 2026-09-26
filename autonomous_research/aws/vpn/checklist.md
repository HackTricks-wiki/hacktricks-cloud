# VPN (Client VPN / Site-to-Site) — open ideas

`aws-vpn-post-exploitation` is currently an **empty stub** — needs real content or removal.

- [ ] **Client VPN** — `ec2:ExportClientVpnClientConfiguration` / `ExportClientVpnClientCertificateRevocationList`:
  pull the client config (endpoint, DNS, split-tunnel, auth mode) for recon.
- [ ] **Authorization-rule abuse** — `ec2:AuthorizeClientVpnIngress` to grant an attacker
  client-VPN association access to CIDRs it shouldn't reach (lateral into the VPC). Verify min-perms.
- [ ] **Route/target-network tamper** — `CreateClientVpnRoute` / `AssociateClientVpnTargetNetwork`
  to bridge the VPN endpoint into a sensitive subnet (persistence-flavored network foothold).
- [ ] **Site-to-Site** — `ModifyVpnConnection` / `ModifyVpnTunnelOptions` (rekey, PSK): can an
  attacker with these perms MITM or re-establish a tunnel to attacker infra? Assess vs. real value.
- [ ] Decide stub disposition: if none of the above clears the no-garbage bar as a distinct
  technique, **delete the empty stub** rather than leave a dead page.
