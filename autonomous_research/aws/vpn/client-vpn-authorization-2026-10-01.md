# AWS Client VPN authorization-rule audit — 2026-10-01

## Result

Verified and published an exact-endpoint network-authorization escalation: `ec2:AuthorizeClientVpnIngress` alone can add an all-authenticated-users rule for an attacker-chosen destination CIDR. The restricted caller had no Client VPN read, route, association, endpoint-modification, revoke, IAM or ACM permission.

This is expected functionality, not an AWS defect. The impact is bounded to an existing Client VPN endpoint that accepts an attacker-controlled identity and already has the target association/route/security path needed to reach the destination. No client connected and no packet traversed the fixture.

## Safe fixture

- Region: `us-east-1`.
- One isolated certificate-authentication Client VPN endpoint with client CIDR `10.253.0.0/22`.
- No target-network association, route, elastic network interface, connection logging destination, client session or traffic.
- Two two-day self-signed test certificates imported into ACM for the server and mutual-authentication root chain.
- One disposable IAM user with only:

```json
{
  "Effect": "Allow",
  "Action": "ec2:AuthorizeClientVpnIngress",
  "Resource": "arn:aws:ec2:us-east-1:228478051196:client-vpn-endpoint/<fixture-id>"
}
```

The endpoint reached `pending-associate`, which is the expected state without a subnet/Transit Gateway association. AWS Client VPN pricing charges endpoint associations and active connections; neither existed during this test.

## Authorization result

The exact-action user submitted:

```bash
aws ec2 authorize-client-vpn-ingress \
  --client-vpn-endpoint-id <fixture-id> \
  --target-network-cidr 10.250.0.0/16 \
  --authorize-all-groups \
  --description ht-clientvpn-rule-audit \
  --region us-east-1
```

The API returned `authorizing`; administrator inventory then observed the rule become:

```json
{
  "DestinationCidr": "10.250.0.0/16",
  "AccessAll": true,
  "GroupId": "",
  "Status": "active",
  "Description": "ht-clientvpn-rule-audit"
}
```

The same caller received `UnauthorizedOperation` for both `DescribeClientVpnAuthorizationRules` and `RevokeClientVpnIngress`, with the denial naming the exact endpoint ARN. Therefore neither read nor cleanup permission is an implicit dependency of the write. The rule also did not require a pre-existing target-network association or route to be created; those remain prerequisites for useful traffic rather than API authorization dependencies.

## Impact boundaries

- Authorization rules grant network access only to clients that already authenticate to the endpoint. The write does not mint a mutual-TLS certificate, add an AD/SAML user, or alter the endpoint authentication methods.
- An all-groups rule authorizes every authenticated client for the CIDR. A group-specific rule requires the correct AD SID or SAML group value.
- The endpoint still needs a route and target-network path. An existing VPC subnet association normally supplies a local VPC route. Other destinations can require a separately authorized `CreateClientVpnRoute`, peering/transit/on-premises connectivity and route-table changes.
- Security groups, NACLs, host firewalls and application authentication continue to apply.
- A rule can reset active endpoint connections and may take time to propagate, adding availability and detection side effects.
- This is private-network lateral movement / network-plane authorization escalation, not control-plane IAM escalation.

## Telemetry

After the normal indexing delay, Event History confirmed `AuthorizeClientVpnIngress` and `RevokeClientVpnIngress` as default EC2 management writes. The successful authorization request stored a nested `AuthorizeClientVpnIngressRequest` containing exact endpoint ID, description, destination CIDR, generated client token and `AuthorizeAllGroups:true`; its response stored status `authorizing`. The administrator revoke stored endpoint, destination and `RevokeAllGroups:true` and returned `revoking`.

The restricted caller's denied revoke also retained the complete endpoint/CIDR/all-groups request, returned `Client.UnauthorizedOperation`, and named the exact endpoint ARN and missing action in the message. The denied describe named the same exact ARN. The active rule remained directly visible through administrator `DescribeClientVpnAuthorizationRules`. Use should be correlated with Client VPN connection logs, VPC Flow Logs, firewall/DNS telemetry and target application/service logs.

Fixture lifecycle events additionally retained the complete endpoint certificate/authentication configuration and returned the generated Client VPN DNS name/state. No certificate private key appeared in the EC2 request or response.

## Rejected/queued variants

| Candidate | Disposition |
| --- | --- |
| Claim the action gives an unauthenticated foothold | Rejected; client authentication remains mandatory |
| Claim rule creation alone makes the CIDR reachable | Rejected; association, route and downstream network controls remain independent |
| `CreateClientVpnRoute` to an additional routed network | Still queued; likely useful only with an existing target association and network path |
| `AssociateClientVpnTargetNetwork` to a sensitive subnet | Still queued; adds cost-bearing association/ENIs and must be tested with exact subnet/VPC authorization and full asynchronous cleanup |
| CRL removal/import to reactivate a revoked certificate | High-value future test for mutual-certificate endpoints; endpoint modifications may take up to four hours |

## Cleanup

The administrator revoked the test rule and independently observed zero matching authorization rules. The endpoint was deleted before any association or client connection was created. Both ACM certificates and the disposable IAM access key, inline policy and user were deleted. Independent final inventories returned zero tagged Client VPN endpoints, zero tagged ACM certificates and zero `ht-clientvpn-rule-*` users.

No subnet, VPC, route, association, ENI, public IPv4 address, log group/stream, directory, SAML provider, Client VPN session or traffic was created.

## References

- [AWS Client VPN authorization rules](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-rules.html)
- [Add a Client VPN authorization rule](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-rule-authorize-add.html)
- [Client authorization](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/client-authorization.html)
- [Client VPN target networks](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-target.html)
- [Client VPN endpoint modifications](https://docs.aws.amazon.com/vpn/latest/clientvpn-admin/cvpn-working-endpoints.html)
- [Amazon EC2 service authorization reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_ec2.html)
- [AWS VPN pricing](https://aws.amazon.com/vpn/pricing/)
