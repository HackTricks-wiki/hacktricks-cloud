# DSCP Configuration — Tests Done

| # | Hypothesis | Minimum permission tested | Status |
|---|------------|---------------------------|--------|
| 1 | Published singular `dscpConfiguration/read` authorizes DSCP create/update | `Microsoft.Network/dscpConfiguration/read` | **REFUTED 2026-09-26** — PUT required hidden plural `dscpConfigurations/write` |

**Lab record (2026-09-26 — invalid-body authorization differential):** Created disposable RG
`htrc-dscpauth-26926`, UAMI `htrc-dscp-mi-26926`, no-ingress ACI
`htrc-dscp-probe-26926`, and a custom role containing only the published singular
`Microsoft.Network/dscpConfiguration/read` action at the test RG.

Using the UAMI's ARM token against API `2025-05-01`:

- collection list returned 200 with an empty list, proving the identity, role scope, and propagation;
- item GET for a nonexistent DSCP configuration returned ARM 403 requiring the unpublished plural
  `Microsoft.Network/dscpConfigurations/read` action;
- item PUT with a deliberately invalid protocol returned ARM 403 requiring the unpublished plural
  `Microsoft.Network/dscpConfigurations/write` action.

The invalid body guaranteed that even if authorization unexpectedly passed, the provider could not
create the object. No DSCP configuration was created. The live provider-operation catalog publishes
only singular `dscpConfiguration/read`, `/write`, and `/join/action`; it gives both read and write the
same create/update description. The actual item routes use plural hidden operation strings. Built-in
Reader's `*/read` pattern should match the hidden item-read action, but does not match the hidden write.

**Conclusion:** this is a provider-catalog/custom-role usability defect, not a Reader privilege
escalation and not worth a public attack entry. Retain it here to avoid repeating the test and to flag
the singular/plural mismatch when auditing custom Network roles.

**Teardown:** deleted the role assignment, ACI, UAMI, custom role, and RG. Confirmed the RG no longer
exists and that all `htrc-*` group/resource and `26926` custom-role inventories are empty.
