# Permission のリスク分類

HackTricks Cloud は、[CloudPEASS](https://github.com/peass-ng/CloudPEASS) と [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) が使用する共有 permission severity データを管理しています。いずれかの consumer にある生成済みコピーではなく、ここにある canonical platform file を編集してください。

- **Critical**: 強力な privileges の直接的、またはほぼ独立した付与、identity の mint、あるいは privileged execution を可能にする permissions。
- **High**: 機密情報、credentials、または条件付きの privilege escalation path へのアクセス。
- **Medium**: DoS/Break、運用上の disruption、通常の変更、または機密データや privilege path が実証されていない条件付き capabilities。
- **Low**: 通常の discovery および metadata へのアクセス。

プラットフォームごとに canonical YAML file が1つあります: [AWS](aws.yaml)、[GCP](gcp.yaml)、[Azure](azure.yaml)、[Kubernetes](k8s.yaml)。これらは machine-readable files であり、platform pages で編集方法を説明しています。

## Cloud provider files

`version` と `provider` は schema を識別します。`permission_categories` には4つの個別 permission lists が含まれます。permission を別の list に移動すると、その rating が変更されます。AWS と Azure の matching は大文字小文字を無視します。GCP の matching では大文字小文字が保持されます。同じ severity 内では case aliases を重複させられますが、矛盾する ratings は拒否されます。

`severity_overrides` には、generic rules に対する監査済みの例外が含まれます。例外が catalog にも存在する場合、両方の entries は一致していなければなりません。`severity_caps` は、組み合わせによって選択した permissions が昇格されるのを防ぎます。`non_permission_identifiers` は、文書化された API-method names、condition keys、その他の実際の authorization permissions ではない文字列を除外します。

`combinations.critical` と `combinations.high` は permission lists の lists です。組み合わせを適用するには、内側の list のすべての要素が grant されていなければなりません。組み合わせはまとめて保持してください。個別の grants に分割すると、risk を過大評価することになります。catalog にない permissions については、既存の exact および regular-expression fields が fallback として残ります。classifier 全体の rewrite や新しい matching behavior には、引き続き consumer 側の code changes が必要です。

## Kubernetes file

`rules` は順序付けされています。最初に matching した rule が適用されます。各 rule には一意の `id`、`match`、`severity`、plain-language の `description` があります。より specific な rule は broader な rule より前に追加するか、既存 rule の severity を変更してください。最後の無条件 fallback は保持してください。

Matches では、構成のために `all`、`any`、`not` を使用するか、`field`、`op`、`value` の比較を使用します。使用可能な fields は、`group`、`resource`、`subresource`、`full`（resource/subresource）、`verb`、`namespace`、`name`、`path`（小文字の non-resource URL）、`non_resource_url`、`mode`、`delegated_verb` です。Operations は `eq`、`ne`、`in`、`not_in`、`contains`、`prefix`、`suffix`、`truthy` です（value は不要）。`always: true` はすべてに matching します。Group、resource、subresource、verb の values は lowercase です。literal wildcard は `'*'` と記述します。wildcard grant との matching は rules 内で明示され、shell pattern expansion は使用されません。

`severity_when` は、matching condition に対して別の severity を任意で選択します。`severity: delegated` は constrained impersonation 用に予約されています。その `delegated_severities` map は delegated action の classification を conditional rating に変換します。Description placeholders では、`{full}` や `{verb}` など、使用可能な fields を参照できます。rules は data であり、Python や shell code として評価されることはありません。

## Validation and synchronization

変更を提出する前に、PyYAML をインストールした状態で `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` を実行してください。book の pull-request workflow でも同じ validation が実行されます。

毎週月曜日に、両方の consumer repositories はこの book の現在の `master` を checkout し、4つの files をすべて validation し、SHA-256 hashes を比較して、bundled YAML files と生成済みの legacy lists を更新します。source manifest には book revision と各 file の hash が記録されます。book への無関係な変更では consumer commit は作成されません。各 workflow は manual run にも対応しています。Tests は workflow が consumer の default branch に変更データを commit する前に実行されます。失敗した場合、その branch は変更されません。更新の間、consumer は offline で bundled copies を使い続けます。

consumer でローカルに更新するには、`python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` を実行してください。書き込みを行わずに stale copies を検出するには `--check` を追加します。
