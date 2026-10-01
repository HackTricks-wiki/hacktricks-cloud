# Client VPN endpoint DNS/routing/logging modification audit — 2026-10-01

## Result

Verified and published a compound `ec2:ModifyClientVpnEndpoint` technique. A caller with only that action on one exact endpoint ARN changed three settings in one request:

- enabled a caller-chosen custom DNS server;
- changed split-tunnel mode from `true` to `false`; and
- disabled existing Client VPN connection logging.

Admin inventory observed all three values within five seconds. The restricted caller could not call `DescribeClientVpnEndpoints` and had no target-network, route, authorization-rule, security-group, ACM, CloudWatch Logs, IAM or PassRole permission.

AWS documents that changing DNS or split-tunnel state resets active connections. After reconnect, a controlled reachable DNS server can receive queries and poison answers, while full-tunnel mode replaces client routes with `0.0.0.0/0`. Useful forced egress still requires the endpoint's target association, authorization rule/route and VPC egress path. DNS control does not bypass TLS/application authentication. Disabling Client VPN connection logs suppresses future session request/result/failure/termination telemetry but does not erase existing logs or other control/data-plane sources.

This is service-level persistence, traffic-policy manipulation and defense evasion, not IAM or account persistence.

## Exact authorization boundary

The live user had only:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:ModifyClientVpnEndpoint",
      "Resource": "arn:aws:ec2:us-east-1:228478051196:client-vpn-endpoint/cvpn-endpoint-0e4bfda99a880e114"
    }
  ]
}
```

`DescribeClientVpnEndpoints` returned `UnauthorizedOperation`. The accepted CLI request was:

```bash
aws ec2 modify-client-vpn-endpoint \
  --region us-east-1 \
  --client-vpn-endpoint-id cvpn-endpoint-0e4bfda99a880e114 \
  --dns-servers 'CustomDnsServers=192.0.2.53,Enabled=true' \
  --connection-log-options Enabled=false \
  --no-split-tunnel
```

The DNS value is an IANA documentation address; no resolver existed there and no traffic was sent.

## Safe fixture

- Region: `us-east-1`
- Run/user prefix: `ht-clientvpn-modify-20261001044340`
- Endpoint: `cvpn-endpoint-0e4bfda99a880e114`
- Client CIDR: `10.250.0.0/22`
- Initial split tunnel: enabled
- Initial connection logging: enabled to a new empty log group/stream
- Initial DNS servers: none
- Authentication configuration: mutual certificate authentication with a short-lived CA and ACM server certificate
- Target-network associations: none
- Authorization rules/routes/client certificates/sessions: none

Five seconds after the write, administrator inventory returned the semantic state:

```json
{
  "Dns": ["192.0.2.53"],
  "Split": false,
  "Logging": false
}
```

Because the endpoint had no target association or client identity, the test exercised only the control plane: no session was reset and no network or DNS packet was generated.

## CloudTrail evidence

- Event time: `2026-10-01T04:44:12Z`
- Event name: `ModifyClientVpnEndpoint`
- Event ID: `cf8f6d8a-963e-468a-b44a-a50e61dfc7a4`
- Request ID: `02e5ab6b-7d0f-4c92-ad78-314acbc8d0dd`
- Caller: `arn:aws:iam::228478051196:user/ht-clientvpn-modify-20261001044340`
- `readOnly:false`
- `managementEvent:true`

The default management event identifies the endpoint and the response returns success. Defenders should correlate every such uncommon write with an immediate endpoint inventory snapshot and preserve the prior state; connection resets and routing/DNS effects, existing CloudWatch logs, VPC Flow Logs, DNS/firewall/IDS and destination-service logs provide additional signals.

A separate unexpected audit-content completeness issue was confirmed during event-shape validation. Details are withheld from the public repository and retained only in a restricted local AWS report pending disclosure.

## Cleanup

The restricted access key/policy/user, endpoint, ACM certificate, empty CloudWatch log group/stream, and every local CA/server key and certificate file were deleted.

Independent final inventory returned:

```text
endpoint=[] cert=[] iam=[] log_group=[] local_dir=no
```

No target association, ENI, route, authorization rule, client certificate, session, traffic, public IP or external resolver existed. There is no cost or cleanup debt.

## Disposition

- Expected endpoint-control composition: published in the VPN post-exploitation page.
- Unexpected audit-record completeness issue: recorded privately and not disclosed in the public technique.
- No other unexpected Client VPN endpoint-modification malfunction was observed.
