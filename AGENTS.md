# AGENTS.md

将来このリポジトリで作業するエージェント向けのガイダンス。

## Repository Context

これは HackTricks Cloud の mdBook リポジトリです。関連するメインブックは以下にあります:

`/Users/carlospolop/git/hacktricks`

共有テーマ/search の動作を変更する場合は、両方のリポジトリに適用する必要があることがあります。

## Search Index Loading Contract

カスタム search UI は以下にあります:

`theme/ht_searcher.js`

生成済みのコピーが以下にある場合もあります:

`book/theme/ht_searcher.js`

本番環境がすでにビルド済みの `book/` ディレクトリをデプロイしている場合は、両方のコピーを更新するか、デプロイ前に book を再ビルドしてください。

search index の読み込み順序は重要で、コストにも影響します:

1. GitHub リポジトリから各言語固有および fallback の search index をすべて読み込む:
`HackTricks-wiki/hacktricks-searchindex`
2. すべての GitHub ホスト候補が失敗した場合のみ、同一オリジンの mdBook 出力に fallback する。

local の `/searchindex.js` fallback を、`searchindex-cloud-en.js.gz` のような GitHub ホストの fallback より前に置かないでください。production で `cloud.hacktricks.wiki` から `searchindex.js` を配信すると高コストです。

このリポジトリでは、期待される local fallback は以下です:

`/searchindex.js`

このリポジトリの main-book fallback は以下です:

`/searchindex-book.js`

このファイルはあくまで fallback です。primary source は、`HackTricks-wiki/hacktricks-searchindex` 内の remote `searchindex-<lang>.js.gz` および `searchindex-cloud-<lang>.js.gz` ファイルのままにしてください。

## Search Index Publishing

`HackTricks-wiki/hacktricks-searchindex` に暗号化された圧縮 search index を publish する workflows は以下です:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成元の source file は `book/searchindex.js` です。publish される remote artifact 名は以下です:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader は、`theme/ht_searcher.js` で定義された key を使った XOR-encrypted gzip payload の remote `.js.gz` ファイルを期待しています。

## Build And Validation

一般的な local check は以下です:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` が失敗した場合は、以下を確認してください:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 検索には `rg` を優先してください。
- 明示的に要求されない限り、生成された `book/` の出力はコミットに含めないでください。すでにビルド済みのページを直ちに修正する必要がある場合は、search loader の修正は例外です。
- 共有テーマの動作を変更する場合は、`/Users/carlospolop/git/hacktricks` の対応するファイルも比較して更新してください。
- 関連のない local changes は revert しないでください。
