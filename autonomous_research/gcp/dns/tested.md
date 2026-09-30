# Cloud DNS — tested

## 2026-09-28 documentation audit

Documentation-only validation against current official Google Cloud and Google Workspace documentation and the installed `gcloud dns` command surface. No APIs were enabled and no cloud resources were read or changed.

- Reduced the post-exploitation page from twelve overlapping H3s to seven distinct techniques: public record mutation, private-zone shadowing, outbound server-policy redirection, response-policy local-data override, query-log surveillance/blinding, forwarding/peering zones, and DNSSEC availability impact.
- Corrected record-write authorization to the required pair: `dns.changes.create` plus the relevant `dns.resourceRecordSets.create`, `.update`, or `.delete` permission.
- Added the missing attachment gates: `dns.networks.bindPrivateDNSZone`, `dns.gkeClusters.bindPrivateDNSZone`, `dns.networks.bindPrivateDNSPolicy`, `dns.networks.bindDNSResponsePolicy`, and `dns.gkeClusters.bindDNSResponsePolicy`. Peering also requires `dns.networks.targetWithPeeringZone` on the producer network.
- Corrected name-resolution boundaries: GKE cluster-scoped policies/zones precede the VPC order; a VPC outbound server policy precedes VPC response policies, private/peering zones, internal DNS, and public DNS; response-policy local data otherwise overrides private, public, and internal DNS.
- Removed claims that DNS redirection automatically bypasses TLS or steals metadata tokens. Redirection supports denial of service or interception only when the application protocol, trust, and endpoint reachability permit it.
- Corrected forwarding semantics: standard routing can use the internet for public targets, while private routing always traverses the authorized VPC and requires a privately reachable target and the documented `35.199.192.0/19` return path.
- Corrected query logging: it is a product-log stream rather than Cloud Audit Logs, cached answers might not each be logged, Shared VPC private query logs belong to the host project, and disabling logging does not delete retained entries.
- Corrected the audit model: Cloud DNS writes are always-on Admin Activity, but Cloud DNS does have Data Access audit methods for admin reads and DNS-key/operation reads. Removed the previous claim that no Data Access audit surface exists.
- Reframed `dns.managedZones.update` on DNSSEC. Disabling signing while the registrar DS remains produces validation failures and a noisy outage; a safe integrity downgrade requires separate registrar control and correct DS removal/expiry ordering.
- Folded WRR/geo variants into public-record tampering, and GKE bindings into their underlying private-zone/response-policy techniques. Removed the zone-IAM self-grant H3 as privilege escalation and the dangling-name-server H3 as unauthenticated access; retained concise scope notes so they are not mistaken for post-exploitation primitives.
- Validated local help for managed-zone, record-set, server-policy, response-policy, and response-policy-rule create/update surfaces. The installed `policies update --help` omits the documented `--no-enable-logging` spelling, but the current official monitoring guide explicitly documents that command.

Primary sources: Cloud DNS access control, audit logging, records, zone management, VPC name-resolution order, server policies, response-policy API/management, query logging, forwarding/peering zones, routing policies, and DNSSEC configuration; Certificate Manager DNS authorization and Google Workspace administrator recovery for the bounded cross-service effects.

## 2026-09-28 independent cross-review

- Replaced the private-query-log disable command with a direct `policies.patch` call. The Cloud DNS monitoring guide documents `gcloud dns policies update --no-enable-logging`, but both the installed SDK and the current standalone gcloud reference expose only `--enable-logging`. The PATCH is current, requires only `dns.policies.update`, and avoids the helper's prerequisite `dns.policies.get` plus any network-binding revalidation.
- Added the exact audit method for reading query logs: `google.logging.v2.LoggingServiceV2.ListLogEntries` (`DATA_READ`, disabled by default).
- Corrected the current predefined-role holders of `dns.managedZones.setIamPolicy` to Owner, IAM Security Admin, and Admin. The current IAM role catalog does not list the previously claimed service-specific roles.
- Bounded DNSSEC outage timing: validating failures begin when unsigned answers are served while the parent DS remains effective, rather than necessarily immediately after the control-plane update.
- Added the missing data-plane prerequisite for DNS peering reconnaissance: the attacker must be able to issue and observe queries from the consumer network. Clarified that `35.199.192.0/19` handling applies to Type 1/2 VPC-routed targets under standard RFC 1918 routing as well as private routing.
- Removed unrelated response-policy update methods from the add-rule telemetry table and identified `dns.managedZones.patch` as the exact method used by the shown gcloud DNSSEC command.
