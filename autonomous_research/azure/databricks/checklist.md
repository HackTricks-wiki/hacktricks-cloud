# Databricks — Candidate Attacks (not yet lab-fired)

Cost note: Databricks clusters incur DBU + VM cost — verify a single-node job cluster stays <$5/30min
before firing, and tear down immediately.

- [ ] Live-fire notebook/init-script RCE and dump the workspace MSI token via IMDS from the driver;
      confirm what (if anything) lands in Activity Log vs. workspace audit (separate plane).
- [ ] Confirm `updateDenyAssignment` behaviour (UNVERIFIED) — does the workspace RP let a caller alter
      the managed-RG deny assignment to gain direct control-plane access?
- [ ] Test KV-backed secret-scope read as a cross-service credential-access pivot.
