# AGENTS.md

为未来在此 repository 中工作的 agents 提供指导。

## Repository Context

这是 HackTricks Cloud mdBook repository。相关的主 book 位于：

`/Users/carlospolop/git/hacktricks`

对共享 theme/search 行为的更改通常需要同时应用到两个 repository。

## Search Index Loading Contract

自定义 search UI 位于：

`theme/ht_searcher.js`

此外可能还有一个生成的副本：

`book/theme/ht_searcher.js`

如果 production 部署的是已经构建好的 `book/` directory，请更新两个副本，或在部署前重新构建 book。

search index 的加载顺序非常重要，并且会影响成本：

1. 从 GitHub repository 加载所有 language-specific 和 fallback search index：
`HackTricks-wiki/hacktricks-searchindex`
2. 仅当所有 GitHub-hosted candidates 都失败时，才回退到 same-origin mdBook output。

不要将本地 `/searchindex.js` fallback 放在任何 GitHub-hosted fallback（例如 `searchindex-cloud-en.js.gz`）之前。在 production 中从 `cloud.hacktricks.wiki` 提供 `searchindex.js` 的成本很高。

对于此 repo，预期的本地 fallback 是：

`/searchindex.js`

此 repo 的主 book fallback 是：

`/searchindex-book.js`

该文件仅用于 fallback。primary source 必须继续使用 `HackTricks-wiki/hacktricks-searchindex` 中的远程 `searchindex-<lang>.js.gz` 和 `searchindex-cloud-<lang>.js.gz` 文件。

## Search Index Publishing

向 `HackTricks-wiki/hacktricks-searchindex` 发布加密压缩 search index 的 workflows 是：

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成的 source file 是 `book/searchindex.js`。发布的 remote artifact 名称是：

- `searchindex-cloud-v2-en.json.gz`（首选的 compact index）
- `searchindex-cloud-v2-<lang>.json.gz`（首选的 compact index）
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader 优先使用 compact v2 artifact，并将 `.js.gz` artifact 作为 legacy fallback。两者都是使用 `theme/ht_searcher.js` 中定义的 key 进行 XOR-encrypted 的 gzip payload。

## Build And Validation

常用的本地检查：

- `node --check theme/ht_searcher.js`
- `mdbook build`

如果 `mdbook build` 失败，请检查：

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 搜索时优先使用 `rg`。
- 除非明确要求，否则不要将生成的 `book/` output 提交。若必须立即修复已经构建的 pages，search loader 修复除外。
- 如果更改 shared theme behavior，请对比并更新
`/Users/carlospolop/git/hacktricks` 中对应的 file。
- 不要还原无关的本地更改。
