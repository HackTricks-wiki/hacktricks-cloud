# AGENTS.md

このリポジトリで作業する今後のエージェント向けガイダンス。

## リポジトリのコンテキスト

これは HackTricks Cloud mdBook リポジトリです。関連するメインブックは以下にあります。

`/Users/carlospolop/git/hacktricks`

共有テーマや検索動作への変更は、両方のリポジトリに適用する必要がある場合があります。

## Search Index の読み込み契約

カスタム検索 UI は以下にあります。

`theme/ht_searcher.js`

生成済みのコピーが以下に存在する場合もあります。

`book/theme/ht_searcher.js`

production で既にビルド済みの `book/` ディレクトリをデプロイしている場合は、両方のコピーを更新するか、デプロイ前に book を再ビルドしてください。

Search index の source policy は重要であり、コストにも影響します。

- public host では、すべての言語固有および fallback の候補を `HackTricks-wiki/hacktricks-searchindex` からのみ読み込んでください。同一オリジンの mdBook output には fallback しないでください。production で大きな index を `cloud.hacktricks.wiki` から配信するとコストが高くなります。
- localhost、`.local`/`.internal` host、loopback、RFC1918、carrier-grade NAT、link-local、または private IPv6 address では、同一オリジンの mdBook output のみを読み込んでください。これにより、local/container deployment を self-contained に保てます。

この repo で想定される local fallback は以下です。

`/searchindex.js`

この repo の main-book fallback は以下です。

`/searchindex-book.js`

これらの local file は private-network source 専用です。public host では、`HackTricks-wiki/hacktricks-searchindex` にある remote の `searchindex-<lang>.js.gz` および `searchindex-cloud-<lang>.js.gz` file のみを使用してください。

## Search Index の公開

暗号化された圧縮 Search Index を `HackTricks-wiki/hacktricks-searchindex` に公開する workflow は以下です。

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成される source file は `book/searchindex.js` です。公開される remote artifact 名は以下です。

- `searchindex-cloud-v2-en.json.gz`（推奨される compact index）
- `searchindex-cloud-v2-<lang>.json.gz`（推奨される compact index）
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader は compact v2 artifact を優先し、`.js.gz` artifact を legacy fallback として保持します。どちらも、`theme/ht_searcher.js` で定義された key を使用する XOR-encrypted gzip payload です。

loader は lazy のままにしてください。通常の page navigation では、visitor が search を開くか使用するまで、search worker を作成したり index を download したりしてはいけません。remote の圧縮 response は origin ごとに 24 時間 Cache Storage に保存されるため、後続の page で再利用できます。期限切れの entry の refresh に失敗した場合は、stale-cache fallback を維持してください。

## Build と検証

一般的な local check：

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` が失敗した場合は、以下を確認してください。

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## 編集時の注意

- 検索には `rg` を優先してください。
- 明示的に要求されない限り、生成された `book/` output を commit に含めないでください。既にビルド済みの page を直ちに修正する必要がある場合は、Search loader の修正は例外です。
- 共有 theme の動作を変更する場合は、`/Users/carlospolop/git/hacktricks` にある対応する file と比較し、更新してください。
- 関係のない local change を元に戻さないでください。
