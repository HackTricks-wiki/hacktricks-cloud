# Client VPN target-network and route audit — 2026-10-01

## Result

Verified and published a two-action Client VPN network-plane technique:

1. `ec2:AssociateClientVpnTargetNetwork` on one exact endpoint and one exact subnet associated the first target network to an endpoint created without a selected VPC.
2. AWS made the endpoint `available`, set its VPC to the subnet's VPC, created the managed association/ENI, and automatically installed an active route for the entire VPC CIDR.
3. `ec2:CreateClientVpnRoute` on the same exact endpoint and subnet added an attacker-chosen documentation-range route through that association; it became `active`.

This can convert a prepared but unattached endpoint into a VPC entry point or extend an associated endpoint to peered, on-premises, internet, or other routed destinations. It does not bypass client authentication, Client VPN authorization rules, VPC routes, SG/NACL controls, or application authentication. Those prerequisites are explicit in the public technique.

The durable association/routes are service-level persistence, not IAM or account-wide persistence. Association billing, durable inventory, managed ENIs, endpoint state changes and default CloudTrail writes make the technique low-stealth.

## Authorization boundary

The first restricted test deliberately granted both actions only on the endpoint ARN. EC2 rejected `AssociateClientVpnTargetNetwork` with `UnauthorizedOperation` naming the exact subnet ARN. That fixture was deleted without any association.

The successful user had only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:AssociateClientVpnTargetNetwork",
        "ec2:CreateClientVpnRoute"
      ],
      "Resource": [
        "arn:aws:ec2:us-east-1:228478051196:client-vpn-endpoint/cvpn-endpoint-0841b02d2b850921e",
        "arn:aws:ec2:us-east-1:228478051196:subnet/subnet-091d0d246c4277c59"
      ]
    }
  ]
}
```

Observed negative controls:

- `DescribeClientVpnTargetNetworks`: denied;
- `DescribeClientVpnRoutes`: denied;
- `DeleteClientVpnRoute`: denied;
- `DisassociateClientVpnTargetNetwork`: denied.

No VPC, subnet-management, ENI, security-group, endpoint-modification, authorization-rule, IAM, ACM or PassRole action was in the test policy.

## Live fixture and controls

- Region: `us-east-1`
- Run/user prefix: `ht-clientvpn-route-20261001040913`
- Endpoint: `cvpn-endpoint-0841b02d2b850921e`
- Association: `cvpn-assoc-0de294ec48f20879c`
- Pre-existing default VPC: `vpc-027af22d687e33781` (`172.31.0.0/16`)
- Pre-existing subnet: `subnet-091d0d246c4277c59` (`172.31.32.0/20`, more than 4,000 free addresses)
- Client CIDR: `10.252.0.0/22`, non-overlapping
- Extra route: `192.0.2.0/24` (IANA documentation range)
- Mutual-auth server/CA material: short-lived local CA and one ACM server certificate
- Connection logging: disabled because no client was allowed to connect

The endpoint was created without a VPC ID, target association, authorization rule, or client certificate. The restricted association selected the default VPC through the subnet and reached `associated` after approximately 340 seconds. Admin checks then observed:

- endpoint status `available`;
- endpoint VPC ID `vpc-027af22d687e33781`;
- one active automatic route for `172.31.0.0/16`;
- a service-managed target association/ENI.

The restricted route request reached `active` after approximately 70 seconds. The documentation CIDR had no supporting VPC path, no authorization rule existed, and no client certificate was issued, so the route carried no traffic.

## CloudTrail evidence

Both actions were default EC2 management writes with `readOnly:false` and `managementEvent:true`.

| Time (UTC) | Event | Event ID | Request ID |
| --- | --- | --- | --- |
| `2026-10-01T04:09:46Z` | `AssociateClientVpnTargetNetwork` | `da0a20c7-e95d-4046-8673-c741221882a3` | `77afeb88-dd9a-40e4-b48c-f7aa723a62fa` |
| `2026-10-01T04:15:59Z` | `CreateClientVpnRoute` | `50b38db9-8479-4d4f-a62c-55675888f9f7` | `6d6d7cff-09b2-4ff0-ad55-119200d9ce8e` |

The association request retained endpoint ID, subnet ID and generated client token; its response retained association ID, request ID and `associating` status. The route request retained endpoint ID, destination CIDR, target subnet, description and client token; its response retained request ID and `creating` status.

Additional defensive signals include endpoint/association/route inventory, the managed ENI, security-group application, Client VPN association billing, connection logs when enabled, VPC Flow Logs, and downstream DNS/firewall/application telemetry.

## Cleanup

The IAM access key/policy/user were deleted at cleanup start. Admin cleanup deleted the extra route, disassociated the target network, waited until no association remained, deleted the endpoint, deleted the ACM certificate, and removed every local CA/server key and certificate file.

Independent final inventory returned:

```text
endpoint=[] cert=[] iam=[] eni=[] local_dir=no
```

The default VPC and subnet were pre-existing and were not modified. No authorization rule, VPC/subnet/route-table/security-group mutation, client certificate, session, traffic, public IP, instance or external target was created. The short association time stayed far below the authorized cost ceiling and there is no cleanup debt.

## Disposition

- Published as a bounded post-exploitation network-attachment and route technique.
- No unexpected AWS malfunction was found; the subnet-ARN authorization denial was correct and useful.
- No private AWS vulnerability report was created for these expected control-plane actions.
