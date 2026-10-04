# Key Vault — Candidate Attacks (not yet lab-fired)

Move an item to tests-done.md once checked. No duplicates of anything above or on the wiki.

- [ ] Confirm min-perms for private-endpoint **approval** path end-to-end on a firewalled vault.
- [ ] Verify whether `diagnosticSettings/delete` alone (without write) suffices to blind, and what
      residual event the delete itself leaves.
- [ ] `createMode=recover` squat: after a vault is soft-deleted by the owner, confirm an attacker with
      only `vaults/write` in the same sub can recover-and-repopulate it (name-squat persistence).
