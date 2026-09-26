# Vertex Ai — tested

Vertex AI. 20 privesc techniques; post-ex generalised pipeline-spec disclosure across the family.

## VERIFIED LIVE — RAG Engine confused-deputy
- CreateRagCorpus (LRO) → `ragFiles:import` (importedRagFilesCount=1) → `:retrieveContexts` returned
  the object plaintext verbatim. `ragCorpora.query` read-back is in `roles/aiplatform.viewer` (low
  priv). Audit: CreateRagCorpus/DeleteRagCorpus = ADMIN_WRITE (always on); ImportRagFiles +
  RetrieveContexts produced NO activity entry (Data Access off by default) — ingest/read-back silent.
  Infra torn down.

## Excluded
- Dialogflow `agents.export` / conversation-transcript exfil — borderline, below bar.
