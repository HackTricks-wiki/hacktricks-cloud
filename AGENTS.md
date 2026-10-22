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

The search index source policy is important and cost-sensitive:

- On public hosts, load every language-specific and fallback candidate only from
  `HackTricks-wiki/hacktricks-searchindex`. Never fall back to the same-origin mdBook output;
  serving the large index from `cloud.hacktricks.wiki` in production is expensive.
- On localhost, `.local`/`.internal` hosts, loopback, RFC1918, carrier-grade NAT, link-local, or
  private IPv6 addresses, load only the same-origin mdBook output so local/container deployments
  remain self-contained. For a non-English page, try the language-prefixed local path first (for
  example `/es/searchindex.js`) and use the root English index only as a fallback.

For this repo, the expected local fallback is:

`/searchindex.js`

The main-book fallback for this repo is:

`/searchindex-book.js`

Those local files are private-network sources only. Public hosts must use the remote
`searchindex-<lang>.js.gz` and `searchindex-cloud-<lang>.js.gz` files in
`HackTricks-wiki/hacktricks-searchindex` exclusively.

## Search Index Publishing

The workflows that publish encrypted compressed search indexes to
`HackTricks-wiki/hacktricks-searchindex` are:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

The generated source file is `book/searchindex.js`. The published remote artifact names are:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

The browser loader prefers the compact v2 artifact and keeps the `.js.gz` artifact as a legacy
fallback. Both are XOR-encrypted gzip payloads using the key defined in `theme/ht_searcher.js`.

The loader must stay lazy: normal page navigation must not create the search worker or download an
index until the visitor opens or uses search. Remote compressed responses are persisted in Cache
Storage for 24 hours per origin so subsequent pages can reuse them. Preserve the stale-cache
fallback when refreshing an expired entry fails.

## Build And Validation

Common local checks:

- `node --check theme/ht_searcher.js`
- `node --test scripts/test_search.js` (matching, ranking, UI, source policy, and cache regressions)
- `HT_SEARCH_CORPUS=1 node --test scripts/test_search.js` (also checks both generated books when present)
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

## Book Organization Notes

- Document each technique in one place, alongside related techniques, and link to it from other
  pages that need it. Do not duplicate techniques.
- Keep pages readable as the book grows. Group related techniques, and split pages when they
  become too long. Avoid creating a separate page for every small technique.

## Content Syntax and Format Notes

- Use simple English that non-native speakers can understand.
- Be direct and remove sentences that do not add useful information.
- Explain complex topics from the beginning, including the context, examples, and code needed
  to understand them. Keep simple additions brief when the surrounding page already explains
  the topic.
- After writing an explanation, check whether someone with basic IT knowledge could understand
  it. Add missing context when needed.
- Start paragraphs by explaining the idea and its context before stating a conclusion or rule.
  For example, explain why offsets vary between kernel builds before telling readers not to
  reuse them.
- When editing a page, correct nearby content that does not follow these guidelines.

## Branch hygiene

- **Use the configured default branch.** Check the repository setting; it may be `main`, `master`, or something else. Base ordinary work on it and merge approved changes back into it. Target release branches only when required. Respect reviews, checks, and branch protection.
- **Create only needed branches.** Check `git status` and worktrees first. Use one short-lived branch per change, reuse it for revisions, and preserve others' work. Avoid speculative or duplicate branches.
- **Clean up after a verified merge.** Confirm the changes landed, including after squash/rebase, and that no open PR or unmerged work needs the branch. Delete only your completed task's remote/local branch and worktree; prune stale refs. Never delete default, protected, shared, or unrelated branches.
- **Leave a clean environment.** Check for leftover branches, worktrees, and uncommitted changes. Clean up safely or explain what must remain; never merge or delete when authorization or safety is uncertain.
