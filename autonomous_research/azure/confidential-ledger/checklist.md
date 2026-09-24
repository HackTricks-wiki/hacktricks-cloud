# Confidential Ledger — Candidate Attacks (not yet lab-fired)

Cost note: verify hourly cost before provisioning; if over gate, keep DOC-ONLY.

- [ ] Provision a ledger and confirm `ledgers/write` lets a control-plane caller self-grant a
      data-plane security principal (Administrator role) without a separate data-plane grant (UNVERIFIED).
- [ ] Confirm `filesExport/action` produces an attacker-readable export and whether the append-only
      guarantee still lets an attacker read all historical entries.
