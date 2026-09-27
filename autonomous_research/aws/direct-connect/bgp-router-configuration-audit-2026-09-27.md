# Direct Connect BGP/router-configuration audit — 2026-09-27

## Result

Confirmed from the current API model and AWS's own CLI workflow that
`DescribeVirtualInterfaces` returns both a plaintext `authKey` and `customerRouterConfig`; the latter
contains the same value in `<bgp_auth_key>`. `DescribeRouterConfiguration` independently returns the
customer router configuration for a selected virtual interface.

This is expected functionality and a useful credential-access technique, not a vulnerability report.
The BGP TCP-MD5 key is reusable by a party able to configure/reach the customer-side BGP peer, but the
read alone does not create network reachability, reveal a MACsec CAK, or bypass physical, VLAN,
routing, security-group, NACL or on-path requirements.

## Authorization and detection

The current Service Authorization Reference maps `DescribeRouterConfiguration` to `dxvif` resources
and maps `DescribeVirtualInterfaces` to connection, LAG and virtual-interface resource types; both
support `aws:ResourceTag`. Direct Connect records all API calls as CloudTrail management events.
AWS's published `DescribeVirtualInterfaces` example has `responseElements: null`, so the read is
detectable but the returned secret is not duplicated in the CloudTrail event.

## Live lab boundary

In `us-east-1`, the authorized account returned:

- zero connections;
- zero LAGs;
- zero Direct Connect gateways;
- zero virtual interfaces; and
- zero gateway association proposals.

The gateway-association list operation requires a gateway/association selector and therefore cannot
serve as an unfiltered account-wide list. An unsigned `DescribeVirtualInterfaces` request returned
`MissingAuthenticationTokenException`. CloudTrail lookup returned Direct Connect management-event
history, confirming the event source `directconnect.amazonaws.com`.

No physical connection or billable fixture was provisioned, and no resource or configuration was
created, changed or left behind.

## Documentation decision

- Added a dedicated enumeration page because the previous four-command subsection omitted the BGP
  secret, router configuration, cross-account gateway state, physical handoff, MACsec posture and
  logging behavior.
- Added the BGP credential-retrieval technique to post-exploitation with explicit network/on-path
  limitations.
- Split the established cross-account gateway path into the persistence section while retaining the
  full command and actor-boundary explanation on the post-exploitation page.

## Official sources

- <https://docs.aws.amazon.com/directconnect/latest/APIReference/API_DescribeVirtualInterfaces.html>
- <https://docs.aws.amazon.com/directconnect/latest/APIReference/API_DescribeRouterConfiguration.html>
- <https://docs.aws.amazon.com/directconnect/latest/UserGuide/using-cli.html>
- <https://docs.aws.amazon.com/directconnect/latest/UserGuide/vif-router-config.html>
- <https://docs.aws.amazon.com/directconnect/latest/UserGuide/ts-layer-3.html>
- <https://docs.aws.amazon.com/directconnect/latest/UserGuide/logging_dc_api_calls.html>
- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_directconnect.html>
