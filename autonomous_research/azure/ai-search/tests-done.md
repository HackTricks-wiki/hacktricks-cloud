# AI Search — Tests Done

Wiki: `az-ai-search-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `debugSessions/write`+execute on-demand skillset detonation / MI-token exfil | those actions | **UNVERIFIED** (skill-invoke) |
| 2 | `searchServices/write` re-enable-auth / open-net / attach-identity | that action | DOC-ONLY |
| 3 | `indexes/write` schema-poison + vectorizer-repoint | that action | **UNVERIFIED** (vectorizer-repoint) |
| 4 | sharedPrivateLink / privateEndpoint | those actions | DOC-ONLY (note) |
