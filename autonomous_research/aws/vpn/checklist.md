# VPN (Client VPN / Site-to-Site) — open ideas

The former empty stub now documents the valuable Standard-storage Site-to-Site VPN PSK download path.

- [ ] **Client VPN** — `ec2:ExportClientVpnClientConfiguration` / `ExportClientVpnClientCertificateRevocationList`:
  pull the client config (endpoint, DNS, split-tunnel, auth mode) for recon.
- [x] **Authorization-rule abuse** — exact-endpoint `ec2:AuthorizeClientVpnIngress` alone added an all-authenticated-users rule for a chosen CIDR. The caller could not list or revoke it. Published with the client-auth, association, route, security-group/NACL and application-auth boundaries; live fixture fully cleaned 2026-10-01.
- [ ] **Route/target-network tamper** — `CreateClientVpnRoute` / `AssociateClientVpnTargetNetwork` to bridge the VPN endpoint into a sensitive subnet (persistence-flavored network foothold).
- [ ] **Site-to-Site** — `ModifyVpnConnection` / `ModifyVpnTunnelOptions` (rekey, PSK): can an attacker with these perms MITM or re-establish a tunnel to attacker infra? Assess vs. real value.
- [x] **Site-to-Site configuration download** — `GetVpnConnectionDeviceSampleConfiguration` discloses live Standard-storage PSKs; Secrets Manager storage redacts them and remains a separate `GetSecretValue` boundary. Public page added with bounded network-position prerequisites.
- [x] Stub disposition: populated with the PSK disclosure technique.
