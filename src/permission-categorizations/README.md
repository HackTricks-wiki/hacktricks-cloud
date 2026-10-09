# Permissionリスク分類

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloudは、[CloudPEASS](https://github.com/peass-ng/CloudPEASS)と[Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS)が利用する共有のpermission severityデータを管理しています。いずれかのconsumerにある生成済みコピーではなく、ここにあるプラットフォームごとの正規ファイルを編集してください。

- **Critical**: 強力な権限を直接、またはほぼ単独で付与する、identityを作成する、あるいは特権実行を可能にするpermission。
- **High**: 機密情報やcredentialへのアクセス、または条件付きのprivilege escalation経路。
- **Medium**: DoS/Break、運用上の妨害、通常の変更、または機密データや権限への経路が実証されていない条件付き機能。
- **Low**: 通常の探索とmetadataへのアクセス。

プラットフォームごとに正規のYAMLファイルが1つあります: [AWS](aws.yaml)、[GCP](gcp.yaml)、[Azure](azure.yaml)、[Kubernetes](k8s.yaml)。これらは機械可読ファイルです。プラットフォームのページでは、ブラウザー上にYAML全体を表示し、編集方法を説明しています。インラインviewerはbook内のコピーを使用し、PEASSのworkflowはGitHubから正規ファイルを取得します。

## Cloud providerファイル

`version`と`provider`はschemaを識別します。`permission_categories`には、4つのpermissionリストが格納されています。permissionを別のリストに移動すると、その評価が変わります。AWSとAzureの照合では大文字と小文字を区別しません。GCPの照合では区別します。同じseverity内では、大文字と小文字の違いだけのaliasを重複して登録できますが、評価が競合する場合は拒否されます。

`severity_overrides`には、監査済みの汎用ルールの例外が格納されています。例外がcatalogにも存在する場合、両方の項目で評価を一致させる必要があります。`severity_caps`は、permissionの組み合わせによって評価が引き上げられるのを防ぎます。`non_permission_identifiers`は、文書化されたAPI method名、condition key、その他の実際のauthorization permissionではない文字列を除外します。

`combinations.critical`と`combinations.high`は、permissionリストのリストです。内側のリストのすべての要素が付与されている場合に、その組み合わせが適用されます。組み合わせはまとめたままにしてください。個別のgrantに分割すると、リスクを過大評価することになります。既存の完全一致フィールドと正規表現フィールドは、catalogにないpermissionに対するfallbackとして引き続き使用されます。classifier全体の書き換えや、新たな照合動作の追加には、consumer側のコード変更が必要です。

## Kubernetesファイル

`rules`は順序付きです。最初に一致したruleが適用されます。各ruleには、一意の`id`、`match`、`severity`、平易な説明である`description`が必要です。より具体的なruleをより広範なruleより前に追加するか、既存ruleのseverityを変更してください。最後の無条件fallbackは維持してください。

照合条件は、組み合わせに`all`、`any`、`not`を使用するか、`field`、`op`、`value`による比較を使用します。使用できるfieldは、`group`、`resource`、`subresource`、`full`（resource/subresource）、`verb`、`namespace`、`name`、`path`（小文字のnon-resource URL）、`non_resource_url`、`mode`、`delegated_verb`です。演算子は`eq`、`ne`、`in`、`not_in`、`contains`、`prefix`、`suffix`、`truthy`（valueは不要）です。`always: true`はすべてに一致します。Group、resource、subresource、verbの値は小文字です。ワイルドカードを文字として指定する場合は`'*'`と記述します。ワイルドカードgrantへの一致はruleで明示し、shellのpattern展開には頼りません。

`severity_when`を指定すると、一致条件に応じて別のseverityを選択できます。`severity: delegated`は、制約付きimpersonation専用です。その`delegated_severities` mapは、delegated actionの分類を条件付きの評価に変換します。説明文のplaceholderでは、`{full}`や`{verb}`など、使用可能なfieldを参照できます。ruleはデータであり、Pythonやshellのコードとして評価されることはありません。

## 検証と同期

変更を提出する前に、PyYAMLをインストールしたうえで`python scripts/sync_hacktricks_permissions.py --book-root . --validate-only`を実行してください。bookのpull request workflowでも同じ検証が実行されます。

毎週月曜日に、両方のconsumer repositoryはこのbookの最新の`master`をcheckoutし、4つすべてのファイルを検証してSHA-256 hashを比較し、同梱のYAMLファイルと生成済みのlegacy listを更新します。source manifestにはbookのrevisionと各ファイルのhashが記録されます。bookに無関係な変更があっても、consumer側にcommitは作成されません。各workflowは手動実行にも対応しています。workflowが変更されたデータをconsumerのdefault branchにcommitする前に、testが実行されます。失敗した場合、そのbranchは変更されません。更新の合間も、consumerはofflineで同梱コピーを使い続けます。

consumer内でローカルに更新するには、`python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`を実行してください。書き込みを行わず古いコピーを検出するには、`--check`を追加してください。

両方のconsumerにおけるsourceの取得では、checkoutの制限時間を設定し、待機時間を段階的に延ばしながら5回再試行します。不完全なdownloadは一時ディレクトリに保持されます。再試行を使い切っても、既存の同梱データは変更されません。
{{#include ../banners/hacktricks-training.md}}
