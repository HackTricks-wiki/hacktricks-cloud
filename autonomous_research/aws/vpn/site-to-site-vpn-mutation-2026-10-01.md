# Site-to-Site VPN peer-mutation audit — 2026-10-01

## Result

Verified and published a bounded network-plane takeover chain using two expected EC2 features:

1. `ec2:ModifyVpnConnection` on one exact VPN connection ARN changed its customer gateway to a second gateway backed by a controlled public IP.
2. The connection returned to `available` with the replacement customer gateway while retaining its AWS tunnel endpoints and existing Standard-storage PSKs.
3. `ec2:ModifyVpnTunnelOptions` on the same exact VPN ARN replaced one selected tunnel PSK with a caller-chosen value.
4. After the second update returned to `available`, the authoritative customer-gateway configuration contained the replacement PSK.

The limited caller had no describe, create, delete, route, VPC, gateway, Elastic IP, IAM, Secrets Manager, KMS, or configuration-download permission. `DescribeVpnConnections` was an explicit denied negative control.

This is useful only with the surrounding network prerequisites. The attacker needs a pre-existing customer gateway whose public IP they control, or separate permission to create one; a compatible VPN appliance; the tunnel outside IPs and settings; and an existing usable route/security path. If the existing Standard PSKs are already known, the customer-gateway swap may be sufficient. Otherwise, rotating both tunnels with `ModifyVpnTunnelOptions` supplies known credentials one tunnel at a time.

The technique is network-plane access and service-level persistence, not IAM privilege escalation or account-wide persistence. The configuration remains until a defender restores the customer gateway and credentials. Both actions also have direct availability impact because endpoint replacement interrupts tunnels.

## Exact authorization boundary

The live user had only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:ModifyVpnConnection",
        "ec2:ModifyVpnTunnelOptions"
      ],
      "Resource": "arn:aws:ec2:us-east-1:228478051196:vpn-connection/vpn-0128aee56cc7157d6"
    }
  ]
}
```

Observed controls:

| Operation | Result |
| --- | --- |
| `DescribeVpnConnections` as the restricted user | `UnauthorizedOperation` |
| `ModifyVpnConnection` to known replacement customer gateway | Accepted |
| Admin describe after stabilization | `available`, replacement customer-gateway ID present |
| Admin configuration check after gateway swap | Replacement controlled public IP present; original PSK preserved |
| `ModifyVpnTunnelOptions` for known outside IP with selected PSK | Accepted |
| Admin configuration check after stabilization | Selected replacement PSK present |

The service authorization reference lists `vpn-connection*` as the required resource type for both actions. No customer-gateway ARN was needed in the limited policy.

## Disposable fixture

- Region: `us-east-1`
- Run tag/user prefix: `ht-s2s-mutate-20261001032833`
- VPN connection: `vpn-0128aee56cc7157d6`
- Original customer gateway: `cgw-0de761e183c91fcbd`
- Replacement customer gateway: `cgw-03719b6217f23ae4e`
- Virtual private gateway: `vgw-0f72ddbbe76ff727c`
- Two short-lived Elastic IP allocations supplied controlled, unique customer-gateway public IPs.
- The VGW was never attached to a VPC.
- No VPN route was created.
- No customer appliance or IPsec process was running.
- Both tunnels remained DOWN and no data traffic was sent.

Control-plane timings in this test were slow but conclusive:

- initial VPN creation reached `available` after approximately 340 seconds;
- customer-gateway replacement reached `available` after approximately 660 seconds;
- one-tunnel PSK replacement was visible in the available configuration after approximately 200 seconds.

These timings reinforce that the technique is noisy and availability-affecting rather than stealthy.

## CloudTrail evidence

Both restricted-user mutations were default EC2 management writes with `readOnly:false` and `managementEvent:true`.

| Time (UTC) | Event | Event ID | Request ID |
| --- | --- | --- | --- |
| `2026-10-01T03:35:32Z` | `ModifyVpnConnection` | `29cc5e3b-d5ac-4ba0-868e-706b81f1e60f` | `b92324f8-3dcd-419a-bfe0-648a22dfe31d` |
| `2026-10-01T03:47:43Z` | `ModifyVpnTunnelOptions` | `0492e4cc-0332-4c3a-b858-4248c046bb51` | `8cd906cb-80dd-4441-8918-0991adb56461` |

The first request identified the VPN connection and replacement customer gateway. The second identified the VPN connection, selected outside tunnel IP, and tunnel-options object. Tunnel state/inventory changes, CloudWatch VPN metrics, optional tunnel logs, BGP/static-route effects, and downstream network telemetry are additional defensive signals on a real connection.

A separate unexpected security-impact issue was found while validating the contents and authorization boundary of the audit records. Exploit details are withheld from the public repository and retained only in the restricted local AWS report pending disclosure.

## Cleanup

The mutation user, inline policy and access key were deleted first. The VPN connection was deleted and observed `deleted`; both customer gateways, the virtual private gateway and both Elastic IP allocations were then deleted/released. Cleanup retried the VGW deletion to handle EC2's asynchronous dependency release.

Independent final inventory returned:

```text
vpn=[] cgw=[] vgw=[] eip=[] iam=[]
```

No VPC attachment, route, instance, customer appliance, tunnel session or traffic existed. The short-lived connection and EIPs stayed far below the authorized cost ceiling. There is no cleanup debt.

## Disposition

- Expected gateway/PSK mutation chain: published in the VPN post-exploitation page.
- Public claims: bounded to Standard-storage PSKs and the explicit network/routing prerequisites.
- Unexpected audit-content boundary: recorded privately, not published in the book or this ledger.
- No other unexpected Site-to-Site VPN control-plane malfunction was observed.
