# Privilege escalation paths

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud は、[Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) が利用する、機械可読な privilege escalation カタログを管理しています。各 technique には、principal がどのリソースに対してどの権限を実効的に持つ必要があるか、また、どの target principal の権限を得られるかが記載されています。Blue-CloudPEASS は、読み取り専用のインベントリスナップショットをオフラインで評価し、権限を付与する policy または binding を根拠として principal 間の攻撃経路を描画するとともに、その経路を取り除く mitigation を示します。consumer 側のコピーではなく、ここにある正規ファイルを編集してください。

各エントリには、前提条件、到達可能な target、mitigation のみを記載します。コマンド、payload、実行手順は含みません。technique の詳細は、リンク先の HackTricks ページを参照してください。

## Layout

platform ごとに 1 つのディレクトリ（`aws`、`gcp`、`azure`、`k8s`）があり、service ごとに 1 つの `<service>.yaml` ファイルがあり、それぞれ technique の YAML リストを格納します。`_excluded*.yaml` という名前のファイルには、post-exploitation、persistence、設定からモデル化できない technique など、意図的にエントリを設けていない、確認済みの HackTricks technique を理由とともに記載します。`privesc-technique.schema.json` は、エディターの入力補完と検証に使う JSON Schema のエクスポート版です。

## Technique fields

- `id`: 全体で一意な、小文字の kebab-case 形式の ID。platform 名を接頭辞にします。
- `provider`、`service`、`title`、`summary`: source が何を得るかを説明する 1 文。
- `source`: technique を説明する、この書籍内の相対パスとアンカー。`source_revision` は参照した書籍の commit です。
- `requires`: source が保持すべき権限。`all_of` には必須項目をすべて列挙し、`any_of` には代替項目を列挙します。AWS と GCP の項目では `action` と `resource`、Azure の項目では `action`（または `data_action`）と `scope`、Entra ID の項目では `entra_permission` または `entra_role`、Kubernetes の項目では `verb`、`resource`、`subresource`、`api_group`、`namespace` を使います。`{target.arn}` のような placeholder は、要件を target に紐付けます。
- `target`: target の `kind`、principal が到達可能となるためにすべての条件を満たす必要がある `selector`、およびその `scope`。
- `conditions` と `blockers`: condition key、SCP、boundary、admission policy など、実際には経路を妨げる可能性があるもの。
- `confidence`、`severity`、`mitigation`、`references`、任意の `notes`。

未知のフィールド、target kind、selector key、placeholder は無視されず拒否されます。そのため、エントリによって target の範囲が暗黙に広がったり狭まったりすることはありません。新しい selector を追加する場合は、まず consumer の evaluator でサポートしてください。

### Schema v2 joins

v2 loader では、2 つの placeholder と 1 つの AWS selector が追加され、既存の K8s running-pod selector を GCP target でも使用できるようになりました。これらのフィールドには、収集済みインベントリとの正確な join が必要です。インベントリが不足している場合、到達可能な経路とはせず、coverage は unknown になります。

| Field | Use and required shape |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` と `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | AWS の `aws_account_admin` target で併用します。すべての要件の代替項目に、この placeholder に対する `iam:CreatePolicyVersion` が含まれている必要があります。policy は、source が同じアカウント内で assume できる role にアタッチされている必要があります。evaluator は policy version の容量を確認し、role の実効権限を再計算します。`SetDefaultPolicyVersion` は対象外です。 |
| `target.selector.k8s_sa_used_by_running_pod: true` | `scope: cluster` の GCP `k8s_service_account` target で使用し、一致した GKE cluster 内で、利用可能な token を持つ running pod が使用している KSA を選択します。`k8s_sa_in_cluster` または `k8s_sa_has_token_secret` と併用しないでください。既存の K8s での使用方法に変更はありません。 |
| `{source_rolebound_clusterrole}` | `api_group: rbac.authorization.k8s.io` と `namespace: "*"` を指定した K8s `clusterroles` 要件の `resource_name` として使用します。各代替項目には、同じ名前に対する `escalate` と `update` または `patch` が必要です。target は `scope: same_namespace` かつ `selector.k8s_sa_in_namespace: "{target.namespace}"` の `k8s_service_account` でなければなりません。また、RoleBinding がその namespace 内の source を bind している必要があります。 |

## Validation and synchronization

変更を提出する前に、PyYAML をインストールした環境で `python scripts/validate_privesc_paths.py --book-root .` を実行してください。このスクリプトは、ディレクトリ構成、evaluator の strict loader（Blue-CloudPEASS の schema module のコピーである `scripts/privesc_paths_schema.py`）による全エントリの検証、一意な ID、source ページと見出しアンカー、JSON Schema が最新であることを確認します。`--peaso-root /path/to/Blue-CloudPEASS` を指定すると、両方の schema ファイルが consumer とバイト単位で一致することも確認できます。書籍の pull request workflow でも同じ検証を実行します。

毎週月曜日、Blue-CloudPEASS はこの書籍の最新の `master` を checkout してこれらのファイルを検証し、各ファイルの SHA-256 hash を前回の同期時に記録された hash と比較します。上流で追加、更新、削除されたファイルは、変更されていない consumer 側のコピーを置き換えます。両側で変更されたファイルは conflict として報告され、確認済みの ledger に明記されない限り、technique ID が削除されることはありません。コンテンツが無効、またはテストに失敗した場合、consumer の default branch は変更されません。書籍に加えられた無関係な変更によって、consumer の commit が作成されることはありません。
{{#include ../banners/hacktricks-training.md}}
