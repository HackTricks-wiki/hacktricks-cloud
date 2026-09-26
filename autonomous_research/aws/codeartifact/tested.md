# CodeArtifact — tested

## 2026-09-26 bearer-token authorization boundaries

- **Repository binding: secure.** Two 15-minute tokens minted by a role with `ReadFromRepository` on only repository `allow` returned HTTP 200 from `allow` and HTTP 403 from sibling repository `deny` in the same domain. An unauthenticated request and a one-character-mutated token returned HTTP 401.
- **Live IAM revocation: secure.** After adding an explicit deny for `ReadFromRepository` on `allow`, IAM simulation reported `explicitDeny` immediately. Existing and newly minted bearer tokens still returned 200 during a short propagation window at 0.7 seconds, then all returned 403 at 7.6 seconds. An administrator token continued returning 200, proving repository health.
- No new public-book technique and no private AWS vulnerability report: behavior matches AWS documentation.
- Full matrix, request IDs, constraints, and cleanup: `token-boundaries-2026-09-26.md`.

