# Application Design Center — open ideas

## Current public coverage

- [x] Map the regional space, catalog/template/revision, application-template/component/connection,
      shared-template and application hierarchy plus the Infrastructure Manager deployment path.
- [x] Map all six live MCP tools and verify anonymous schema discovery, anonymous invocation denial,
      the independent `mcp.tools.call` gate and the underlying Design Center permission gate.
- [x] Live-verify that project-level `roles/designcenter.viewer` directly lists and reads objects in
      a known bucket while project bucket enumeration remains denied.
- [x] Document Design Center, MCP and Storage audit layers and verify no read records appear under an
      empty Data Access audit configuration.
- [x] Remove the object/bucket, test identity/key/config, three IAM grants, API enablement and every
      local response artifact; verify exact zero residue.

## Safe live-validation leads

- [ ] In an already configured disposable management project, reduce each Design Center read to its
      exact permission and capture representative synthetic IaC, topology and assessment fields.
      Export nothing from a real application and delete every synthetic template/application.
- [ ] Bind Viewer on an owned disposable folder containing two synthetic projects and confirm normal
      Storage permission inheritance, IAM Conditions, deny-policy and VPC-SC boundaries. Treat any
      access outside IAM inheritance as private-first.
- [ ] Enable Data Access only in a disposable fixture and capture exact v1 method names for IaC
      export, catalog source fetch and MCP wrapper calls. Restore the audit policy afterwards.
- [ ] Re-diff the six MCP schemas for new deployment, import or setup arguments and repeat the
      wrapper/backend matrix. Never invoke `setup_adc` merely to test MCP authorization because it
      creates persistent space, bucket and App Hub state.

## Private-first authorization candidates

- [ ] With a prepared zero-risk deployment service account and synthetic template, verify that both
      the caller and Design Center service agent must retain `iam.serviceAccounts.actAs`. Any deploy
      or preview beyond caller authority is report-only until coordinated disclosure.
- [ ] Test Cloud Storage IaC import against an owned cross-project bucket using separate caller and
      service-agent permissions. Expected behavior is strict source object IAM; any confused-deputy
      read is private-first.
- [ ] Compare application, template, component and connection access across two spaces with distinct
      resource IAM. Treat cross-space or cross-management-project disclosure as private-first.

## Do not promote without distinct impact

- [ ] Do not turn ordinary read-only template/application enumeration into multiple weak techniques;
      retain it as context unless synthetic results prove a distinct secret/topology disclosure.
- [ ] Do not describe documented application deployment as arbitrary service-account escalation;
      the published workflow requires explicit deployment-SA authorization and downstream roles.
- [ ] Do not label anonymous MCP tool schemas a foothold; they reveal only public operation schemas.
