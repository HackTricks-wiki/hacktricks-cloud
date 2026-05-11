# AGENTS.md

面向在此仓库中工作的未来 agents 的指导。

## Repository Context

这是 HackTricks Cloud mdBook 仓库。相关的主书位于：

`/Users/carlospolop/git/hacktricks`

对共享 theme/search 行为的更改，通常需要在两个仓库中都应用。

## Search Index Loading Contract

自定义 search UI 位于：

`theme/ht_searcher.js`

也可能有一个生成的副本位于：

`book/theme/ht_searcher.js`

如果 production 正在部署已经构建好的 `book/` 目录，请更新这两个副本，或者在部署前重新构建 book。

search index 的加载顺序很重要，而且对成本敏感：

1. 先从 GitHub 仓库加载所有按语言区分的和 fallback 的 search index：
`HackTricks-wiki/hacktricks-searchindex`
2. 只有当所有 GitHub 托管的候选项都失败后，才回退到同源的 mdBook 输出。

不要把本地的 `/searchindex.js` fallback 放在任何 GitHub 托管的 fallback 之前，例如
`searchindex-cloud-en.js.gz`。在 production 中从 `cloud.hacktricks.wiki` 提供 `searchindex.js` 代价很高。

对于这个仓库，预期的本地 fallback 是：

`/searchindex.js`

主书的 fallback 是：

`/searchindex-book.js`

该文件只是 fallback。主要来源必须仍然是远程
`searchindex-<lang>.js.gz` 和 `searchindex-cloud-<lang>.js.gz` 文件，位于
`HackTricks-wiki/hacktricks-searchindex`。

## Search Index Publishing

发布加密压缩 search index 到 `HackTricks-wiki/hacktricks-searchindex` 的 workflows 是：

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成的源文件是 `book/searchindex.js`。发布到远程的 artifact 名称是：

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

浏览器 loader 期望远程 `.js.gz` 文件是使用 `theme/ht_searcher.js` 中定义的 key 的 XOR-encrypted gzip payloads。

## Build And Validation

常见的本地检查：

- `node --check theme/ht_searcher.js`
- `mdbook build`

如果 `mdbook build` 失败，检查：

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 搜索时优先使用 `rg`。
- 除非明确要求，不要把生成的 `book/` 输出提交到 commits 中。Search loader 修复是一个例外，因为如果已经构建好的 pages 必须立即修正。
- 如果修改共享 theme 行为，请对比并更新 `/Users/carlospolop/git/hacktricks` 中的匹配文件。
- 不要回滚无关的本地更改。
