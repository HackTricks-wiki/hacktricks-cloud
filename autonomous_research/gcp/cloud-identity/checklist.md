# Cloud Identity research checklist

## Completed

- [x] Separate Cloud Identity Groups authorization from GCP IAM permissions and OAuth scopes.
- [x] Verify `MEMBER`, `MANAGER`, and `OWNER` semantics and fold non-distinct role transitions.
- [x] Verify current stable membership CLI and v1 API behavior.
- [x] Bound direct user, service-account, nested-group, security-group, and locked-group membership.
- [x] Document external membership as a Domain Restricted Sharing loophole.
- [x] Reconcile Workspace Groups, Enterprise Groups, optional Cloud Logging sharing, and exact
  membership/join/settings event names.
- [x] Remove false anonymous public member-list enumeration and retain public archive recon.
- [x] Bound public self-join versus request/approval flows.
- [x] Verify Groups Settings `whoCanJoin` values, OAuth scope, tenant-policy boundary, and audit event.
- [x] Reconcile key, IAM Credentials, OAuth token, Access Evaluation, Workspace product, and GCP
  downstream attribution for domain-wide delegation.
- [x] Confirm new DWD authorization is super-admin persistence, not service-account-creation privesc.
- [x] Review whether a distinct Cloud Identity post-exploitation H3 meets the no-garbage bar.
- [x] Independently cross-review default versus customized membership authorization and the
  administrator-only security/locked-group boundaries.
- [x] Revalidate current stable `gcloud identity groups` search, membership, transitive, and graph
  flags against local CLI help.
- [x] Bound DWD Access Evaluation edition/actor/parameter behavior, Cloud Logging sharing, and the
  cross-GCP-organization client-ID inference.

## Safe future validation

- [ ] In a disposable licensed Workspace tenant, capture direct user, external user, service
  account, and nested-group additions by an owner and manager. Confirm the exact role restrictions,
  LRO completion, legacy Groups event, Enterprise Groups event, and optional Cloud Logging entry.
- [ ] Test attempts by `MEMBER` and `MANAGER` to grant `OWNER`; verify API errors and customized
  **Who can manage members** behavior without touching production groups.
- [ ] Compare regular, security, dynamic, and locked groups for external user/service-account and
  cross-domain nested-group restrictions.
- [ ] Bind a synthetic group to a harmless custom role, add/remove synthetic internal and external
  members, measure IAM propagation/revocation, then remove the IAM binding and group.
- [ ] Change `whoCanJoin` on a synthetic unprivileged group and capture `groups` and
  `groups_enterprise` reports plus Cloud Logging sharing behavior; restore the original setting.
- [ ] Test a public conversation archive and public/direct self-join using synthetic content only;
  verify that the authoritative member list remains unavailable anonymously.
- [ ] In separate disposable GCP/Workspace tenants, authorize a narrow read-only DWD scope, exercise
  key-based and `signJwt` token minting, and capture `SignJwt`, `allow_token_impersonation`, product
  audit actor/application fields, and a Cloud-scoped downstream call. Revoke DWD and delete the key
  and service account immediately.
- [ ] Verify whether every DWD token exchange emits Access Evaluation events across supported
  Workspace editions and record latency/retention before treating that signal as exhaustive.
