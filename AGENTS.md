# AGENTS.md

このリポジトリで作業する将来のエージェント向けガイダンス。

## リポジトリのコンテキスト

これは HackTricks Cloud mdBook リポジトリです。関連するメインブックは次の場所にあります。

`/Users/carlospolop/git/hacktricks`

共有テーマや検索動作への変更は、両方のリポジトリに適用する必要がある場合があります。

## 検索インデックス読み込みの契約

カスタム検索 UI は次の場所にあります。

`theme/ht_searcher.js`

生成済みのコピーが次の場所にも存在する場合があります。

`book/theme/ht_searcher.js`

本番環境でビルド済みの `book/` ディレクトリをデプロイしている場合は、両方のコピーを更新するか、デプロイ前に book を再ビルドしてください。

検索インデックスの読み込み順序は重要であり、コストにも影響します。

1. GitHub リポジトリ `HackTricks-wiki/hacktricks-searchindex` から、言語固有および fallback の検索インデックスをすべて読み込む。
2. GitHub でホストされている候補がすべて失敗した場合にのみ、同一オリジンの mdBook 出力へ fallback する。

`searchindex-cloud-en.js.gz` など、GitHub でホストされている fallback より前に、ローカルの `/searchindex.js` fallback を配置しないでください。本番環境で `cloud.hacktricks.wiki` から `searchindex.js` を配信するにはコストがかかります。

このリポジトリで想定されるローカル fallback は次のとおりです。

`/searchindex.js`

このリポジトリのメインブック用 fallback は次のとおりです。

`/searchindex-book.js`

このファイルは fallback にすぎません。プライマリソースは、`HackTricks-wiki/hacktricks-searchindex` にあるリモートの `searchindex-<lang>.js.gz` および `searchindex-cloud-<lang>.js.gz` ファイルのままにしてください。

## 検索インデックスの公開

暗号化および圧縮された検索インデックスを `HackTricks-wiki/hacktricks-searchindex` に公開する workflow は次のとおりです。

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

生成元ファイルは `book/searchindex.js` です。公開されるリモート artifact 名は次のとおりです。

- `searchindex-cloud-v2-en.json.gz` （推奨される compact index）
- `searchindex-cloud-v2-<lang>.json.gz` （推奨される compact index）
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

ブラウザー loader は compact v2 artifact を優先し、`.js.gz` artifact を legacy fallback として保持します。どちらも `theme/ht_searcher.js` で定義された key を使用する XOR-encrypted gzip payload です。

loader は lazy のままにする必要があります。通常のページ移動では、訪問者が検索を開くか使用するまで search worker を作成したり、インデックスをダウンロードしたりしてはいけません。リモートの圧縮レスポンスは origin ごとに 24 時間、Cache Storage に保存されるため、後続のページで再利用できます。期限切れのエントリの更新に失敗した場合は、stale-cache fallback を維持してください。

## ビルドと検証

一般的なローカルチェック：

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` が失敗した場合は、次を確認してください。

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## 編集に関する注意事項

- 検索には `rg` を優先して使用してください。
- 明示的に要求されない限り、生成された `book/` 出力を commit に含めないでください。すでにビルド済みのページを直ちに修正する必要がある場合は、検索 loader の修正は例外です。
- 共有テーマの動作を変更する場合は、`/Users/carlospolop/git/hacktricks` にある対応するファイルを比較して更新してください。
- 関係のないローカル変更を元に戻さないでください。
