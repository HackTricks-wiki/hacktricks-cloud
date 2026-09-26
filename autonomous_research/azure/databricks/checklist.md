# Databricks — Candidate Attacks (not yet lab-fired)

Cost note: Databricks clusters incur DBU + VM cost — verify a single-node job cluster stays <$5/30min
before firing, and tear down immediately.

- [ ] Live-fire notebook/init-script RCE and dump the workspace MSI token via IMDS from the driver;
      confirm what (if anything) lands in Activity Log vs. workspace audit (separate plane).
- [ ] Test KV-backed secret-scope read as a cross-service credential-access pivot.

<!-- Cleared 2026-09-25: `updateDenyAssignment` (row 7) REFUTED and documented — Geneva-only, and the
     managed-RG deny assignment's dataActions:['*'] neutralises any Storage data-role self-grant. -->
