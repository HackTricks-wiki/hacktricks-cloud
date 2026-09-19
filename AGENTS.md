# AGENTS.md

供未来在此 repository 中工作的 agents 参考的指南。

## Repository 上下文

这是 HackTricks Cloud mdBook repository。相关的主 book 位于：

`/Users/carlospolop/git/hacktricks`

对共享 theme/search 行为的更改通常需要同时应用到两个 repository。

## Search Index 加载契约

自定义 search UI 位于：

`theme/ht_searcher.js`

也可能存在一个生成的副本：

`book/theme/ht_searcher.js`

如果 production 部署的是已经构建好的 `book/` directory，请更新两个副本，或在部署前重新构建
book。

Search index 的加载顺序非常重要，并且会影响成本：

1. 从 GitHub repository 加载所有 language-specific 和 fallback search index：
`HackTricks-wiki/hacktricks-searchindex`
2. 仅当所有 GitHub-hosted candidate 都失败时，才回退到 same-origin mdBook output。

不要将本地 `/searchindex.js` fallback 放在任何 GitHub-hosted fallback（例如
`searchindex-cloud-en.js.gz`）之前。production 中从 `cloud.hacktricks.wiki` 提供
`searchindex.js` 的成本很高。

对于此 repo，预期的本地 fallback 是：

`/searchindex.js`

此 repo 的 main-book fallback 是：

`/searchindex-book.js`

该文件仅用于 fallback。primary source 必须保持为
`HackTricks-wiki/hacktricks-searchindex` 中的远程
`searchindex-<lang>.js.gz` 和 `searchindex-cloud-<lang>.js.gz` 文件。

## Search Index 发布

将加密压缩的 search index 发布到 `HackTricks-wiki/hacktricks-searchindex` 的 workflow
是：

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成的 source file 是 `book/searchindex.js`。发布的远程 artifact 名称为：

- `searchindex-cloud-v2-en.json.gz`（首选的 compact index）
- `searchindex-cloud-v2-<lang>.json.gz`（首选的 compact index）
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader 优先使用 compact v2 artifact，并将 `.js.gz` artifact 作为 legacy
fallback。两者都是使用 `theme/ht_searcher.js` 中定义的 key 进行 XOR-encrypted 的 gzip
payload。

loader 必须保持 lazy：普通页面 navigation 不得创建 search worker，也不得下载 index，直到
visitor 打开或使用 search。远程压缩 response 会按 origin 持久化在 Cache Storage 中，保存
24 小时，以便后续页面复用。刷新过期 entry 失败时，必须保留 stale-cache fallback。

## 构建和验证

常用的本地检查：

- `node --check theme/ht_searcher.js`
- `mdbook build`

如果 `mdbook build` 失败，请检查：

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## 编辑说明

- 搜索时优先使用 `rg`。
- 除非明确要求，否则不要将生成的 `book/` output 提交到 commits 中。当必须立即修正已经构建的页面时，search loader 修复是例外。
- 如果更改共享 theme 行为，请对比并更新
`/Users/carlospolop/git/hacktricks` 中对应的 file。
- 不要回滚无关的本地更改。
