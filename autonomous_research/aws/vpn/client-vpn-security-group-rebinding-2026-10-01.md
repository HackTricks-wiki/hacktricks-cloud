# Client VPN security-group rebinding audit — 2026-10-01

## Result

Verified and published `ec2:ApplySecurityGroupsToClientVpnTargetNetwork` as a bounded network-plane authorization-escalation technique.

AWS documents that Client VPN security groups are associated with its service-managed network interfaces, and protected application SGs commonly allow traffic by referencing the Client VPN SG. The tested action fully replaced the endpoint's default group with a caller-selected exact SG. On a real endpoint, choosing a pre-existing trusted/privileged SG can make VPN traffic satisfy downstream SG-reference rules without changing those target applications.

The action does not change SG rules and does not bypass Client VPN authentication, network-based authorization rules, route/association requirements, NACLs, or application authentication. Those remain explicit prerequisites. The durable endpoint group change is service-level persistence, not IAM or account-wide persistence.

## Exact authorization boundary

The successful user had only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:ApplySecurityGroupsToClientVpnTargetNetwork",
      "Resource": [
        "arn:aws:ec2:us-east-1:228478051196:client-vpn-endpoint/cvpn-endpoint-01d152698f2cea9bc",
        "arn:aws:ec2:us-east-1:228478051196:security-group/sg-0e3e8ce5c3f0be87c",
        "arn:aws:ec2:us-east-1:228478051196:vpc/vpc-027af22d687e33781"
      ]
    }
  ]
}
```

Controls:

- `DescribeClientVpnEndpoints`: denied.
- Apply the pre-existing default SG `sg-0dd2e1241fd3e3a93`: denied specifically on that ungranted SG ARN.
- Apply the exact allowed replacement SG `sg-0e3e8ce5c3f0be87c`: accepted.
- Admin endpoint inventory within five seconds: only the replacement SG present.
- Independent observation during teardown: endpoint still stored only the replacement SG while the association was `disassociating` and the managed ENI had already disappeared.

No general EC2/VPC read, SG-rule write, target association, route, authorization-rule, endpoint modification, IAM, ACM or PassRole action was granted to the restricted user.

## Safe fixture

- Region: `us-east-1`
- Run/user prefix: `ht-clientvpn-sg-20261001042542`
- Endpoint: `cvpn-endpoint-01d152698f2cea9bc`
- Association: `cvpn-assoc-0925df776ee397ae1`
- Pre-existing VPC: `vpc-027af22d687e33781`
- Pre-existing subnet: `subnet-091d0d246c4277c59`
- Initial default SG: `sg-0dd2e1241fd3e3a93`
- Disposable replacement SG: `sg-0e3e8ce5c3f0be87c`
- Client CIDR: `10.251.0.0/22`
- Authentication configuration: mutual certificate authentication with a short-lived local CA and ACM server certificate

The disposable replacement SG had no privileged ingress rule and was not referenced by any application SG. No client certificate or authorization rule was created, so no client could establish a useful data path. The test proved only the intended control-plane identity replacement.

The association reached `associated` after approximately 350 seconds. Admin inventory confirmed the default SG before mutation and the replacement SG five seconds after the restricted write.

## CloudTrail evidence

Both the denied and successful calls were default EC2 management events with `readOnly:false` and `managementEvent:true`.

| Time (UTC) | Result | Event ID | Request ID |
| --- | --- | --- | --- |
| `2026-10-01T04:32:37Z` | Denied for ungranted default SG | `7e1f6789-78a6-4ce2-82ab-df1e4e0b86df` | `afb41647-bcf4-4a31-838a-b156b552acb9` |
| `2026-10-01T04:32:39Z` | Successful replacement SG | `5b5266e4-a3f7-4b48-a386-447ef56ba1bd` | `dca1e6d2-7d92-4168-9eaf-706438f2fd06` |

The request records endpoint ID, VPC ID and the complete SG list. The success response repeats the applied SG IDs and request ID. The denial contains `Client.UnauthorizedOperation` and names the ungranted SG resource.

Additional signals are the endpoint/ENI security-group inventory change and any subsequent connection, VPC Flow Log, firewall/IDS, DNS or destination-application activity.

## Cleanup

The IAM key/policy/user were deleted, then the association was disassociated and observed draining. The endpoint, managed ENI, ACM certificate, replacement SG, and every local CA/server key and certificate file were deleted.

Independent final inventory returned:

```text
endpoint=[] cert=[] iam=[] sg=[] eni=[] local_dir=no
```

The default VPC, subnet and default SG were pre-existing and unchanged. No authorization rule, route-table rule, application SG reference, client certificate, session or traffic was created. Association time remained far below the authorized cost ceiling and there is no cleanup debt.

## Disposition

- Expected AWS functionality with a meaningful security composition; published in the VPN post-exploitation page.
- No unexpected AWS malfunction was observed and no private report was created for this technique.
