# 権限昇格パス

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud は、[Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) が利用する、機械可読な権限昇格カタログを管理しています。各手法には、あるプリンシパルが一連のターゲットプリンシパルの権限を得るために、どのリソースに対してどの権限を実質的に保持する必要があるかが記載されています。Blue-CloudPEASS は、読み取り専用のインベントリスナップショットをオフラインで評価し、権限を付与するポリシーやバインディングを証拠として、プリンシパル間の攻撃パスと、そのパスを取り除く緩和策を図示します。利用側にあるコピーではなく、ここにある正本ファイルを編集してください。

エントリに記載するのは、前提条件、到達可能なターゲット、緩和策のみです。コマンド、ペイロード、実行手順は含まれません。手法の詳細は、リンク先の HackTricks ページを参照してください。

## 構成

プラットフォームごとにディレクトリ（`aws`、`gcp`、`azure`、`k8s`）が1つあり、サービスごとに `<service>.yaml` ファイルが1つあります。各ファイルには、手法の YAML リストが格納されています。`_excluded*.yaml` という名前のファイルには、レビュー済みの HackTricks 手法のうち、ポストエクスプロイテーション、永続化、構成情報からモデル化できない手法など、意図的にエントリを設けていないものと、その理由が記載されています。`privesc-technique.schema.json` は、エディターの補完と検証に使用する、出力済みの JSON Schema です。

## 手法のフィールド

- `id`: プラットフォーム名を接頭辞とする、グローバルに一意な小文字の kebab-case ID。
- `provider`、`service`、`title`、`summary`: ソースが何を取得するかを説明する1文。
- `source`: この手法を説明する HackTricks ページとアンカー。このブックを基準にした相対パスです。`source_revision` は参照したブックのコミットです。
- `requires`: ソースが保持する必要のある権限。`all_of` には必要な項目をすべて、`any_of` には選択肢を列挙します。AWS と GCP の項目では `action` と `resource`、Azure の項目では `action`（または `data_action`）と `scope`、Entra ID の項目では `entra_permission` または `entra_role`、Kubernetes の項目では `verb`、`resource`、`subresource`、`api_group`、`namespace` を使用します。`{target.arn}` などのプレースホルダーは、要件をターゲットに紐付けます。
- `target`: ターゲットの `kind`、プリンシパルが到達可能となるためにすべての条件を満たす必要がある `selector`、およびその `scope`。
- `conditions` と `blockers`: 条件キー、SCP、境界、admission policy など、実際のパスを妨げる可能性のある要素。
- `confidence`、`severity`、`mitigation`、`references`、および任意の `notes`。

未知のフィールド、ターゲットの種類、セレクターキー、プレースホルダーは無視されず、拒否されます。そのため、エントリによってターゲットの範囲が意図せず広がったり狭まったりすることはありません。新しいセレクターを追加する場合は、まず利用側の評価器に対応を追加してください。

## 検証と同期

PyYAML をインストールしたうえで、変更を提出する前に `python scripts/validate_privesc_paths.py --book-root .` を実行してください。このスクリプトはディレクトリ構成、評価器の厳格なローダー（Blue-CloudPEASS のスキーマモジュールのコピーである `scripts/privesc_paths_schema.py`）による全エントリの検証、一意な ID、このブックに各 `source` ページが存在すること、JSON Schema が最新であることを確認します。このブックのプルリクエストワークフローでも同じ検証を実行します。

毎週月曜日に、Blue-CloudPEASS はこのブックの最新の `master` をチェックアウトしてこれらのファイルを検証し、各ファイルの SHA-256 ハッシュを前回の同期時に記録したハッシュと比較します。上流で追加、更新、削除されたファイルは、利用側で変更されていないコピーを置き換えます。両側で変更されたファイルは競合として報告され、レビュー済み台帳に明示的な記録がない限り、手法 ID が削除されることはありません。内容が無効な場合やテストに失敗した場合、利用側のデフォルトブランチは変更されません。このブックに無関係な変更があっても、利用側にコミットは作成されません。
{{#include ../banners/hacktricks-training.md}}
