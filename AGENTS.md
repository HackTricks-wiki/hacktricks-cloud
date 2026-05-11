# AGENTS.md

Guidance for future agents working in this repository.

## Repository Context

This is the HackTricks Cloud mdBook repository. The related main book lives at:

`/Users/carlospolop/git/hacktricks`

Changes to shared theme/search behavior often need to be applied in both repositories.

## Search Index Loading Contract

The custom search UI lives in:

`theme/ht_searcher.js`

There may also be a generated copy at:

`book/theme/ht_searcher.js`

If production is deploying the already-built `book/` directory, update both copies or rebuild the
book before deployment.

The search index loading order is important and cost-sensitive:

1. Load every language-specific and fallback search index from the GitHub repository:
   `HackTricks-wiki/hacktricks-searchindex`
2. Only if all GitHub-hosted candidates fail, fall back to the same-origin mdBook output.

Do not place the local `/searchindex.js` fallback before any GitHub-hosted fallback such as
`searchindex-cloud-en.js.gz`. Serving `searchindex.js` from `cloud.hacktricks.wiki` in production is expensive.

For this repo, the expected local fallback is:

`/searchindex.js`

The main-book fallback for this repo is:

`/searchindex-book.js`

That file is only a fallback. The primary source must remain the remote
`searchindex-<lang>.js.gz` and `searchindex-cloud-<lang>.js.gz` files in
`HackTricks-wiki/hacktricks-searchindex`.

## Search Index Publishing

The workflows that publish encrypted compressed search indexes to
`HackTricks-wiki/hacktricks-searchindex` are:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

The generated source file is `book/searchindex.js`. The published remote artifact names are:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

The browser loader expects the remote `.js.gz` files to be XOR-encrypted gzip payloads using the
key defined in `theme/ht_searcher.js`.

## Build And Validation

Common local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

If `mdbook build` fails, check:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Prefer `rg` for searching.
- Keep generated `book/` output out of commits unless explicitly requested. Search loader fixes are
  an exception when the already-built pages must be corrected immediately.
- If changing shared theme behavior, compare and update the matching file in
  `/Users/carlospolop/git/hacktricks`.
- Do not revert unrelated local changes.
