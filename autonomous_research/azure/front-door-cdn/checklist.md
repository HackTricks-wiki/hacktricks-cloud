# Front Door / CDN — Candidate Attacks (not yet lab-fired)

- [ ] Verify whether Front Door always strips or overwrites a client-supplied `X-Azure-FDID` before the
      origin-bound request, and whether behaviour differs across Classic and Standard/Premium. Use only
      disposable Front Door profiles and an echo origin; keep any surprising trust-boundary result private.
- [ ] Validate cross-tenant re-fronting end-to-end against an origin restricted only to the
      `AzureFrontDoor.Backend` service tag, then confirm that adding the expected `X-Azure-FDID` filter
      blocks the attacker-owned profile.

