# AI Search — Tests Done

Wiki: `az-ai-search-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `skillsets/write` / `debugSessions` WebApiSkill → SSRF + MI-token attach | `skillsets/write` (or `debugSessions/write`+`execute`) | **WORKS (SSRF) / constrained (token)** — verified 2026-09-24 |
| 2 | `searchServices/write` re-enable-auth / open-net / attach-identity | that action | **WORKS** for re-enabling key auth (2026-09-26); network/identity remain DOC-ONLY |
| 3 | `indexes/write` schema-poison + vectorizer-repoint | that action | **WORKS** — live-fire confirmed on wiki (d1527e426): PUT 204 repoints vectorizer `uri`+`authResourceId` in place; query-time token attach, same 2 guardrails |
| 4 | sharedPrivateLink / privateEndpoint | those actions | DOC-ONLY (note) |

**Lab record (test #2, 2026-09-26):** Four temporary Free-tier Search services were created in separate resource groups in `azure-labs-owCfs7hi`. All four groups were deleted and `az group exists` returned `false` for each. No billable Search SKU or other infrastructure was created.

- **Key-auth toggle = WORKS.** Before the change, a listed admin key returned HTTP `200` from `GET /indexes`. A control-plane `PATCH` with `disableLocalAuth:true` changed the stored property to `true` and the same key returned `401` after about ten seconds. A full-resource `PUT` containing `location:eastus`, `sku:free`, `disableLocalAuth:false`, and compatible `authOptions.apiKeyOnly` changed the stored property to `false`; the same key returned `200` at the second ten-second poll. This validates key-auth restoration by `searchServices/write`. The key itself was obtained using the separate `listAdminKeys/action` and was not printed.
- **Two non-working mutations.** A minimal `PATCH` with `disableLocalAuth:false` returned success but a GET still showed `true`; the key stayed at `401`. `az search service update --disable-local-auth true` failed `BadRequest` because it sent the existing `authOptions` together with `disableLocalAuth:true`. Do not recommend either form as a confirmed working toggle. Neither outcome is a security vulnerability on its own.
- **Network opening not tested end-to-end.** Free tier rejected `publicNetworkAccess:disabled` with `Private endpoint access is not supported for the selected SKU free`, so there was no closed network boundary to reopen. The billable-tier network claim remains vendor-doc grounded.
- **Logs.** `az monitor activity-log list` returned `Microsoft.Search/searchServices/write` (Started and Succeeded) and `Microsoft.Search/searchServices/listAdminKeys/action` (Started and Succeeded) after ingestion delay. The first immediate query returned `[]`; the later query after deletion contained the events. Key-authenticated `GET /indexes` requests are data-plane and require AI Search `OperationLogs` diagnostics to be retained.

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
