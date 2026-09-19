# AGENTS.md

この repository で作業する future agents 向けのガイダンス。

## Repository Context

これは HackTricks Cloud mdBook repository です。関連する main book は以下にあります。

`/Users/carlospolop/git/hacktricks`

共有 theme/search behavior の変更は、両方の repository に適用する必要がある場合があります。

## Search Index Loading Contract

custom search UI は以下にあります。

`theme/ht_searcher.js`

以下に generated copy が存在する場合もあります。

`book/theme/ht_searcher.js`

production が既に build 済みの `book/` directory を deploy している場合は、両方の copy を更新するか、deployment 前に book を rebuild してください。

search index source policy は重要であり、cost-sensitive です。

- public hosts では、language-specific および fallback candidate をすべて
`HackTricks-wiki/hacktricks-searchindex` からのみ load してください。同一 origin の mdBook output には決して fallback しないでください。本番環境で大きな index を `cloud.hacktricks.wiki` から serve すると費用がかかります。
- localhost、`.local`/`.internal` hosts、loopback、RFC1918、carrier-grade NAT、link-local、または private IPv6 addresses では、同一 origin の mdBook output のみを load してください。これにより local/container deployments を self-contained に保てます。non-English page では、まず language-prefixed local path（例: `/es/searchindex.js`）を試し、root English index は fallback としてのみ使用してください。

この repo で想定される local fallback は以下です。

`/searchindex.js`

この repo の main-book fallback は以下です。

`/searchindex-book.js`

これらの local files は private-network sources 専用です。public hosts では、`HackTricks-wiki/hacktricks-searchindex` にある remote の `searchindex-<lang>.js.gz` および `searchindex-cloud-<lang>.js.gz` files のみを使用してください。

## Search Index Publishing

encrypted compressed search indexes を
`HackTricks-wiki/hacktricks-searchindex` に publish する workflows は以下です。

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

generated source file は `book/searchindex.js` です。published remote artifact names は以下です。

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader は compact v2 artifact を優先し、`.js.gz` artifact を legacy fallback として保持します。両方とも、`theme/ht_searcher.js` で定義された key を使用する XOR-encrypted gzip payloads です。

loader は lazy のままでなければなりません。通常の page navigation では、visitor が search を開くか使用するまで、search worker を create したり index を download したりしてはいけません。Remote compressed responses は origin ごとに 24 時間 Cache Storage に persist されるため、後続の pages で再利用できます。expired entry の refresh に失敗した場合の stale-cache fallback は維持してください。

## Build And Validation

一般的な local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` が失敗した場合は、以下を確認してください。

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 検索には `rg` を優先してください。
- 明示的に要求されない限り、generated `book/` output を commits に含めないでください。既に build 済みの pages を直ちに修正する必要がある場合は、search loader fixes は例外です。
- shared theme behavior を変更する場合は、
`/Users/carlospolop/git/hacktricks` 内の対応する file と比較し、更新してください。
- 無関係な local changes を revert しないでください。
