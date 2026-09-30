# DSCP Configuration — Candidate Attacks

- [x] Determine whether built-in Reader / exact `Microsoft.Network/dscpConfiguration/read` can call
      the documented DSCP Configuration create-or-update PUT. The live operation catalog gives both
      `dscpConfiguration/read` and `/write` the mutation description, so use an invalid-body
      authorization differential before attempting any valid creation. **REFUTED 2026-09-26:** PUT
      required hidden plural `Microsoft.Network/dscpConfigurations/write`; no resource was created.
- [ ] If read is correctly rejected, verify whether singular/plural resource-type spelling or older
      API versions expose a different authorization mapping.
- [ ] Audit `dscpConfiguration/join/action`: establish which resources can attach a DSCP policy and
      whether join alone can affect traffic classification without configuration write.
