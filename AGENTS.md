# AGENTS.md

供未来在此 repository 中工作的 agents 参考的指南。

## Repository Context

这是 HackTricks Cloud mdBook repository。相关的主书籍位于：

`/Users/carlospolop/git/hacktricks`

对共享 theme/search 行为的更改通常需要同时应用于这两个 repositories。

## Search Index Loading Contract

自定义 search UI 位于：

`theme/ht_searcher.js`

可能还存在一个生成的副本：

`book/theme/ht_searcher.js`

如果 production 部署的是已经构建好的 `book/` directory，请更新两个副本，或在部署前重新构建 book。

search index 的 source policy 很重要，并且涉及成本：

- 在 public hosts 上，仅从
`HackTricks-wiki/hacktricks-searchindex` 加载每种语言的候选项和 fallback。绝不能回退到同源 mdBook output；在 production 中从 `cloud.hacktricks.wiki` 提供大型 index 的成本很高。
- 在 localhost、`.local`/`.internal` hosts、loopback、RFC1918、carrier-grade NAT、link-local 或 private IPv6 addresses 上，仅加载同源 mdBook output，以便 local/container deployments 保持 self-contained。

对于此 repo，预期的 local fallback 是：

`/searchindex.js`

此 repo 的主书籍 fallback 是：

`/searchindex-book.js`

这些 local files 仅作为 private-network sources。Public hosts 必须专门使用
`HackTricks-wiki/hacktricks-searchindex` 中的远程
`searchindex-<lang>.js.gz` 和 `searchindex-cloud-<lang>.js.gz` files。

## Search Index Publishing

将 encrypted compressed search indexes 发布到 `HackTricks-wiki/hacktricks-searchindex` 的 workflows 是：

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成的 source file 是 `book/searchindex.js`。发布的 remote artifact names 是：

- `searchindex-cloud-v2-en.json.gz`（首选的 compact index）
- `searchindex-cloud-v2-<lang>.json.gz`（首选的 compact index）
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader 优先使用 compact v2 artifact，并将 `.js.gz` artifact 保留为 legacy fallback。两者都是使用 `theme/ht_searcher.js` 中定义的 key 进行 XOR-encrypted 的 gzip payload。

loader 必须保持 lazy：正常 page navigation 不得创建 search worker，也不得下载 index，直到 visitor 打开或使用 search。Remote compressed responses 会在每个 origin 的 Cache Storage 中保留 24 小时，以便后续 pages 重用。刷新过期 entry 失败时，必须保留 stale-cache fallback。

## Build And Validation

常用的 local checks：

- `node --check theme/ht_searcher.js`
- `mdbook build`

如果 `mdbook build` 失败，请检查：

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 搜索时优先使用 `rg`。
- 除非明确要求，否则不要将生成的 `book/` output 提交。已经构建的 pages 需要立即修正时，search loader fixes 是例外。
- 如果更改 shared theme behavior，请对比并更新
`/Users/carlospolop/git/hacktricks`
中对应的 file。
- 不要 revert 无关的 local changes。
