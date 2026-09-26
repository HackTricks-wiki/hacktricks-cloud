# Azure ML — Tests Done

Wiki: `az-machine-learning-privesc.md`.

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `listNotebookKeys/read` + `listNotebookAccessToken/read` — Reader-reachable, UNLOGGED notebook-credential theft | `workspaces/*/read` (AzureML Data Scientist) or `*/read` (Reader) | **DOCUMENTED — lab-verified 2026-09-25 (creds returned; ops are `/read`; NOT in Activity Log; file-store canary). Residue: exact download wire-path + Reader-as-principal not fired.** |

**Lab record (2026-09-25):** RG `htrc-mlnb`, workspace `htmlnb11582` (eastus, free — no compute launched),
storage `htmlnb11storage546844941`. `POST .../workspaces/<ws>/listNotebookKeys?api-version=2024-10-01` →
`primaryAccessKey`/`secondaryAccessKey`. `POST .../listNotebookAccessToken` → 8h `access_token`+`refresh_token`,
Bearer scoped `aznb_identity`, host `ml-htmlnb11582-eastus-<guid>.eastus.notebooks.azure.net` (reachable, nginx).
Both ops `isDataAction=false`, names end `/read` (provider metadata) → covered by `workspaces/*/read`
(AzureML Data Scientist) and Reader `*/read`. Notebook file store = default SA `code-<guid>` Files share,
notebooks under `Users/`; planted+read `Users/canary.ipynb` w/ fake API_KEY (via SA key).
**Stealth verified:** neither `read` call appeared in the RG Activity Log (last 1h) while same-session
`/action` siblings (`listStorageAccountKeys/action`, `Storage listKeys/action`) DID — reads excluded from
Activity Log. **Not proven:** (a) exact studioservice download wire-path for `notebooks/storage/download/action`
(proprietary; guessed paths returned "SubscriptionId in bad format" / 404); (b) Reader-as-principal (test SP
mint blocked — session SP lacks Entra directory rights; Reader claim rests on deterministic `*/read` RBAC).
**Teardown:** `az group delete htrc-mlnb`. No test SP was created (creation errored "Insufficient privileges").
