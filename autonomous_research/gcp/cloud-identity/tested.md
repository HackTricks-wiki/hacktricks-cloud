# Cloud Identity security research

## 2026-09-28 — official-contract and local CLI audit

No Workspace, Cloud Identity, Google Group, OAuth client, service account, project, IAM policy, or
API enablement was created or changed. Evidence came from current official Cloud Identity,
Workspace Admin/Reports, IAM, Cloud Logging, Groups Settings, support documentation, and local
stable/beta `gcloud` help.

### Retained findings

- **Membership control over an IAM-bound group (GCP privilege escalation).** A caller with effective
  group membership-management authority can add a controlled user, service account, or nested
  group. Every membership contains `MEMBER`, and GCP IAM ignores the additional Google Groups
  `MANAGER`/`OWNER` role: any direct or transitive member inherits the group's existing IAM roles.
- **External membership is a cross-tenant IAM boundary.** Domain Restricted Sharing constrains the
  allowed group principal but not the identities behind it. If tenant/group policy permits external
  members, adding an external user/service account can therefore undermine DRS. Security groups
  allow external users/service accounts but only same-domain security-group nesting.
- **Open join policy (persistence).** A group owner or manager with effective settings authority and
  an `apps.groups.settings` OAuth scope can set `whoCanJoin=ALL_IN_DOMAIN_CAN_JOIN`; public re-entry
  with `ANYONE_CAN_JOIN` additionally depends on tenant external-member policy. This creates a
  future self-service path into the group's unchanged IAM roles.
- **Public archive reconnaissance (unauthenticated).** Anyone-on-the-web conversation visibility
  can expose archived posts without authentication. Current `whoCanViewMembership` values have no
  public option, so public archive visibility is not anonymous authoritative member enumeration.
- **Public self-join (no victim-tenant credentials).** A Google identity can join an IAM-bound group
  without approval only when the exact tenant/group policy permits it. Request-to-join modes still
  need an approver and were not presented as direct access.
- **Existing DWD abuse.** An actor controlling a delegated service account's key or signing
  authority can mint user-subject tokens only for authorized scopes. IAM Credentials signing is
  Data Access/off by default. Where the tenant edition provides Access Evaluation logs, Workspace
  Reports automatically exposes `allow_token_impersonation` with the service account, subject
  actor, scopes, and DWD source.
- **New DWD grant (persistence, not low-privilege GCP escalation).** A Workspace super administrator
  must authorize the OAuth client ID/scopes. `AUTHORIZE_API_CLIENT_ACCESS` is a default Workspace
  Admin audit event; creating a service account or key has separate GCP Admin Activity.

### Material corrections and rejected/folded claims

- Removed nonexistent project IAM permission requirements
  `cloudidentity.groups.memberships.create` and `.update`. Those are API method concepts; Google
  Group roles/permissions, Workspace administrator authority, or namespace authorization decide
  access, while OAuth scopes constrain the client.
- Removed “modify your membership to OWNER” as a separate GCP escalation. A plain member cannot
  self-promote. By default managers manage non-owner memberships but cannot make an owner; only an
  owner or administrator already capable of group control can grant `OWNER`. Role changes are an
  optional group-control step folded into the membership primitive.
- Folded nested controlled-group membership and dynamic-query manipulation into the single
  membership-control primitive. They do not cross a distinct GCP boundary and have stronger group
  type/licensing prerequisites.
- Corrected audit defaults: membership and role changes are recorded by default in the applicable
  Workspace Groups/Enterprise Groups reports. Only Cloud Logging forwarding is optional. Shared Enterprise
  Groups mutations normalize to
  `google.apps.cloudidentity.groups.v1.MembershipsService.UpdateMembership`; there is no separate
  shareable `CreateMembership` method.
- Corrected join-policy telemetry to Workspace Reports `applicationName=groups`, event
  `change_acl_permission` with `acl_permission=can_join`. That legacy Groups report is not among the
  Workspace streams shareable to Cloud Logging; subsequent joins also appear in Enterprise Groups
  and can be shared.
- Removed `gcloud identity groups memberships add` from the open-join persistence path. That is an
  administrator membership-write command; a principal relying on `whoCanJoin` uses the Google
  Groups self-service **Join group** flow instead.
- Removed anonymous public member-list enumeration. Public conversations are supported; the
  current settings schema permits membership visibility to domain users, members, managers, or
  owners—not the unauthenticated internet.
- Did not create a generic Cloud Identity post-exploitation page. Directory administration or
  membership reading without an IAM-bound group is Workspace administration/reconnaissance, not a
  distinct GCP privilege escalation or sensitive-secret primitive.

### Evidence limits

- Group role permissions can be customized, and tenant sharing policies vary. Documentation gives
  the default manager/owner model; a future live test must inspect each target's effective settings
  rather than infer them from the displayed role alone.
- The official audit catalogs define expected Workspace Reports events and optional Cloud Logging
  mappings. Exact duplicate-event timing across legacy Groups and Enterprise Groups should be
  captured in a disposable licensed Workspace tenant before building strict correlation logic.
- No authorized disposable Workspace/Cloud Identity tenant was available, so cross-domain nesting,
  locked/security-group failures, public join, and DWD actor fields were not live-tested.

### 2026-09-28 — independent reciprocal cross-review

- Corrected group write authorization to distinguish defaults from customized permissions:
  managers manage non-owner memberships by default, but `whoCanModerateMembers=ALL_MEMBERS` can
  extend the primitive to ordinary members and `OWNERS_ONLY` can remove it from managers.
- Made the special-group boundary explicit. Security-group updates require a predefined super
  administrator or Groups administrator, while locked-group core membership changes require an
  administrator authorized for locked groups. Public self-join and ordinary owner/manager paths
  must not be generalized to those group types.
- Clarified that Cloud Identity's documented default can expose authoritative membership details
  to eligible authenticated non-members, subject to customized group and tenant policy, but there
  is no anonymously public `whoCanViewMembership` value.
- Revalidated every retained stable `gcloud identity groups` command against local help. Required
  `--labels`, mutually exclusive `--customer`/`--organization`, and membership/graph flags match
  the current CLI.
- Qualified cross-organization DWD as an inference from the documented exact numeric-client-ID
  workflow and absence of a same-GCP-organization check. The victim tenant's super administrator
  must authorize that exact ID and the actor must still control its signer.
- Corrected Access Evaluation coverage: `allow_token_impersonation` identifies the subject as the
  event actor and separately reports `service_account`, DWD configuration source, and scopes, but
  the log source is edition-dependent and is not listed for Workspace-to-Cloud-Logging sharing.
  Added the exact shared Admin method `google.admin.AdminService.authorizeApiClientAccess` under
  `admin.googleapis.com` for the DWD grant itself.
