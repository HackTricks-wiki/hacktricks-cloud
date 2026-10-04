# Network Management / Network Intelligence Center — open ideas

## Current public coverage

- [x] Map all four live Network Management MCP tools and the separate wrapper authorization gate.
- [x] Prove stored result readback without underlying Compute resource visibility.
- [x] Confirm list responses carry complete stored results and get exposes a known test.
- [x] Capture default create/read/delete telemetry differences.
- [x] Remove every test resource, credential, binding and local artifact and restore the API baseline.

## Open bounded leads

- [ ] In an owned two-project hierarchy, compare trace redaction across Shared VPC, peering and NCC
      when the test creator lacks one path project's Compute Network Viewer. Do not target unrelated
      projects or endpoints.
- [ ] Use disposable rules to compare what a trace reveals about a hierarchical firewall policy
      when the caller cannot read the policy directly; restore all rules/policies immediately.
- [ ] Test a purpose-created internal destination with live probing enabled and correlate VPC Flow
      Logs, firewall telemetry and destination logs; delete the test and all compute assets.
- [ ] Review Cloud Network Insights monitoring-point/path reads for victim-specific hybrid topology
      and monitoring installation material. Keep provider-token generation rejected unless it grants
      a real independent access capability.
- [ ] Re-diff the live MCP tool catalog and Network Management discovery document each release.
