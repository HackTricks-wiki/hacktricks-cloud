# Cloud IDS and network inspection — tested

## 2026-09-28 — current-contract post-exploitation audit

Documentation, public REST discovery schemas, local `gcloud` help, and read-only predefined-role descriptions only. No endpoint, detector, security profile, NSI resource, firewall rule, IAM policy, or other cloud resource was created, updated, or deleted.

### Retained techniques

1. Cloud IDS `UpdateEndpoint` can add `threatExceptions` for selected Palo Alto signature IDs. The sole server-side permission is `ids.endpoints.update`; using `--async` avoids operation polling. The method is an `ADMIN_WRITE` long-running operation in always-on Admin Activity.
2. Cloud NGFW `UpdateSecurityProfile` can assign `ALLOW` to selected threat IDs or severity levels. `ALLOW` transmits the packet and suppresses the threat log; a threat-ID override takes precedence over a severity override. Minimum server permission: `networksecurity.securityProfiles.update`.
3. DNS Threat Detector `excludedNetworks` can omit an attacker-used VPC while other project networks remain covered. The synchronous PATCH returns the updated detector directly. The REST schema and current CLI expose the update. The sole provider is currently Infoblox, so provider “repointing” was removed. The current Cloud NGFW audit catalog does not list DNS Threat Detector methods, so logging is recorded as unverified instead of inferred.
4. NSI in-band integration can route selected victim VPC flows through an already-operational attacker-controlled producer service. The victim chain needs endpoint-group creation, association, custom profile/profile-group creation, and an effective firewall-policy rule. The impact is inline observation/modification/drop; TLS remains a content boundary.
5. NSI out-of-band integration can copy selected traffic to an attacker-controlled collector through the newer `networksecurity` endpoint/association plane plus a Compute packet-mirroring rule. It is distinct from classic `compute.packetMirrorings` and requires the analogous producer-use, endpoint, profile, association, and firewall-policy permissions.

### Removed or corrected

- Removed Cloud IDS endpoint deletion and firewall-endpoint-association deletion: both are destructive, noisy defense-control denial of service and do not independently disclose data, grant privileges, or establish persistence.
- Removed the Cloud IDS endpoint `setIamPolicy` self-grant from post-exploitation. Although IAM role catalogs contain `ids.endpoints.setIamPolicy`, the current public v1 discovery surface exposes no endpoint IAM methods and the Cloud IDS audit catalog lists none. More importantly, a self-grant is persistence/IAM manipulation, not post-exploitation. It is not published until a usable endpoint-level IAM RPC and effective binding behavior are validated.
- Corrected the old IDS role map: `roles/ids.editor` is the dedicated editor role and includes create/update/delete but not `setIamPolicy`; `roles/ids.admin` and Owner include the latter.
- Removed claims that Cloud IDS or Network Security methods were merely “reasoned” Admin Activity methods when exact official catalogs exist. Exact method names and LRO behavior are now cited.
- Correctly labeled DNS Threat Detector as DNS Armor rather than a Cloud NGFW Enterprise resource; both use `networksecurity.googleapis.com` but are documented as different products.
- Corrected NSI minimums. Endpoint-group creation alone does not create a collector or redirect traffic. The attacker needs a usable producer deployment group, producer-side `.use`, a victim VPC association, a custom security profile and group, and an effective firewall/mirroring rule. Producer compute/appliance creation is an additional prerequisite when no attacker-controlled producer already exists.
- Corrected the claim that `roles/networksecurity.admin` alone is sufficient for NSI interception. Compute network/firewall permissions and producer-side authorization are separate boundaries.

Official sources:

- https://docs.cloud.google.com/intrusion-detection-system/docs/configuring-ids
- https://docs.cloud.google.com/intrusion-detection-system/docs/audit-logging
- https://docs.cloud.google.com/iam/docs/roles-permissions/ids
- https://docs.cloud.google.com/firewall/docs/about-security-profiles
- https://docs.cloud.google.com/firewall/docs/audit-logging
- https://docs.cloud.google.com/iam/docs/roles-permissions/networksecurity
- https://docs.cloud.google.com/network-security-integration/docs/in-band/in-band-integration-overview
- https://docs.cloud.google.com/network-security-integration/docs/out-of-band/out-of-band-integration-overview
- https://docs.cloud.google.com/network-security-integration/docs/out-of-band/create-manage-mirroring-rules

## 2026-09-28 — reciprocal review

Independently rechecked the rewrite against current official task guides, REST/audit catalogs, local `gcloud` help, and the installed Cloud SDK command source. No cloud API was invoked and no resource was changed.

- Confirmed that `gcloud ids endpoints update ... --async` submits `UpdateEndpoint` without an endpoint GET or operation poll.
- Confirmed that the displayed `gcloud ... threat-prevention add-override ... --async` path does not fetch the profile first. Its lazy GET is reached only when label-update handling needs the existing labels; the checklist item about a possible unconditional pre-read is resolved.
- Corrected the two Compute audit method names to `v1.compute.networkFirewallPolicies.addRule` and `v1.compute.networkFirewallPolicies.addPacketMirroringRule`. The current Compute audit catalog classifies both as `ADMIN_WRITE` Admin Activity long-running operations gated by `compute.firewallPolicies.update`.
- Removed `networksecurity.securityProfiles.use` from both NSI setup minimums: current task documentation requires `securityProfiles.create` for profile creation and `securityProfileGroups.create` for group creation. Retained `securityProfileGroups.use` for referencing the group from an effective firewall rule.
- Removed `compute.networks.use` from the mirroring minimum. Google documents that permission for intercept associations, but not for mirroring associations; the mirroring path instead uses the association-create permission and endpoint-group use boundary.
- Removed `--async` from dependent NSI creates so the displayed sequence cannot race an unfinished endpoint, association, profile, or group. The page now states the resulting CLI-only `networksecurity.operations.get` requirement and its off-by-default `google.longrunning.Operations.GetOperation` Data Access telemetry; a direct non-polling client retains the smaller server-side mutation set.
- Reconfirmed that DNS Threat Detector methods remain absent from the current Cloud NGFW audit catalog, so the page correctly labels their telemetry unverified.
