# Site-to-Site VPN device-configuration credential audit — 2026-09-26

## Result

Retained `ec2:GetVpnConnectionDeviceSampleConfiguration` as a post-exploitation credential-disclosure technique. AWS's current documentation states that a connection-specific downloaded configuration includes the tunnel PSKs, and its Windows customer-gateway example shows the PSK being used directly for IKE authentication.

The boundary changed in May 2025:

- **Standard storage:** the PSKs remain in the Site-to-Site VPN service and are available through the connection-specific downloaded configuration.
- **Secrets Manager storage:** AWS documents that PSKs in `CustomerGatewayConfiguration` are redacted, returns a managed-secret ARN, and directs operators to retrieve that secret to reveal them. The EC2 getter is not documented as a Secrets Manager authorization bypass.
- **Certificate authentication:** no PSK exists to steal through this path.

The impact is intentionally bounded. A PSK and configuration do not automatically create a working tunnel: the attacker normally needs control of the configured customer-gateway address/network position, or separate permissions to alter the connection/gateway/routing.

## Permission checks

- The service authorization reference lists both `vpn-connection` and `vpn-connection-device-type` as required resource types for `GetVpnConnectionDeviceSampleConfiguration` and classifies it as `List`.
- A disposable role with only `ec2:GetVpnConnectionDeviceSampleConfiguration` on `Resource:"*"` passed IAM evaluation and reached `InvalidVpnConnectionID.NotFound` for a known-bogus ID. No `Describe*` or device-list permission was present.
- Policies scoped to constructed nonexistent resource ARNs returned `UnauthorizedOperation`, including after correcting the documented device-type ARN's account component. This is not evidence against resource scoping: EC2 did not resolve a valid VPN resource for the bogus ID. Exact dual-resource matching was therefore left grounded in the current Service Authorization Reference rather than overclaimed as live-tested.
- The disposable boundary roles and inline policies were deleted after each check.

## Fixture attempts and cleanup

The account initially contained zero Site-to-Site VPN connections in every describable Region.

One unattached virtual-private-gateway/customer-gateway/VPN fixture was created with known disposable PSKs. It remained `pending` for the bounded four-minute window, so no configuration was downloaded. The cleanup trap deleted the VPN and customer gateway; an independent check found the virtual private gateway still `available` because its first delete raced asynchronous VPN deletion. The gateway was immediately deleted on retry and confirmed `deleted`.

A second attempt failed at `CreateVpnConnection` because the newly created virtual private gateway had not reached EC2's consistency boundary. Its cleanup trap removed both preliminary gateways. Independent prefix inventories after both attempts showed:

- zero active tagged VPN connections;
- zero active tagged customer gateways;
- zero active tagged virtual private gateways;
- zero disposable VPN reader/boundary roles.

No VPC was attached, no tunnel reached `available`, no route carried traffic, and no PSK was returned or retained. The brief unattached VPN provisioning attempt stayed far below the testing cost limit.

## Rejected public ideas

- `ExportClientVpnClientConfiguration` is mostly endpoint/certificate/recon material; it does not itself export a client private key or establish a new authorization path. Keep it in the backlog unless a distinct foothold is demonstrated.
- `ExportClientVpnClientCertificateRevocationList` is defensive/recon output, not a useful standalone attack.
- `ModifyVpnTunnelOptions` can rotate a PSK and disrupt a tunnel, but a reliable attacker-owned network foothold also needs customer-gateway/routing control. Do not inflate it into a standalone MITM technique without a tested chain.

## Logging

The getter and device-type discovery are EC2 management reads recorded by CloudTrail. The high-signal detection is any `GetVpnConnectionDeviceSampleConfiguration` outside approved networking automation. Response bytes must be treated as disclosed even after IAM access is revoked; remediation is PSK rotation or migration to Secrets Manager.

## Zero-day assessment

No unexpected AWS malfunction was identified. The Standard-storage download is intentional customer-gateway provisioning behavior, and Secrets Manager storage supplies the expected hardened boundary. This belongs in the public book, not the private vulnerability directory.
