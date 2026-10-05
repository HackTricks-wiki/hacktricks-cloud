# Permission リスクの分類

HackTricks Cloud は、[CloudPEASS](https://github.com/peass-ng/CloudPEASS) と [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) が利用する共有 permission severity データを管理しています。いずれかの consumer にある生成済みコピーではなく、ここにある canonical platform file を編集してください。

- **Critical**: 強力な権限を直接、またはほぼ単独で付与する、identity を mint する、または privileged execution を可能にする permissions。
- **High**: 機密情報や credentials へのアクセス、または条件付きの privilege escalation path。
- **Medium**: DoS/Break、運用上の disruption、通常の変更、または機密データや privilege path が実証されていない条件付き capabilities。
- **Low**: 通常の discovery および metadata access。

platform ごとに canonical YAML file が 1 つあります: [AWS](aws.yaml)、[GCP](gcp.yaml)、[Azure](azure.yaml)、[Kubernetes](k8s.yaml)。これらは machine-readable files です。platform pages では完全な YAML を browser に表示し、編集方法を説明しています。inline viewer は book のコピーを使用し、PEASS workflows は GitHub から canonical files を取得します。

## Cloud provider files

`version` と `provider` は schema を識別します。`permission_categories` には 4 つの個別 permission lists が含まれます。rating を変更するには、permission を別の list に移動します。AWS と Azure の matching では大文字と小文字を区別しません。GCP の matching では大文字と小文字を区別します。同じ severity 内では case aliases を重複させられますが、矛盾する ratings は拒否されます。

`severity_overrides` には、監査済みの generic rules に対する例外が含まれます。例外が catalog にも存在する場合、両方の entries は一致していなければなりません。`severity_caps` は、組み合わせによって選択した permissions の rating が上がることを防ぎます。`non_permission_identifiers` は、documented API-method names、condition keys、および実際の authorization permissions ではないその他の strings を除外します。

`combinations.critical` と `combinations.high` は permission lists の lists です: 内側の list のすべての element が grant されている場合に、その combination が適用されます。combinations はまとめて維持してください。個別の grants に分割すると、risk を過大評価することになります。既存の exact および regular-expression fields は、catalog にない permissions に対する fallback として引き続き使用されます。classifier 全体の rewrite や新しい matching behavior には、引き続き consumers 側の code changes が必要です。

## Kubernetes file

`rules` は順序付けされています: 最初に matching した rule が適用されます。各 rule には一意の `id`、`match`、`severity`、および plain-language の `description` があります。より specific な rule を broader な rule より前に追加するか、既存 rule の severity を変更してください。最後の unconditional fallback は維持してください。

Matches では、composition に `all`、`any`、`not` を使用するか、`field`、`op`、`value` の comparison を使用します。利用可能な fields は `group`、`resource`、`subresource`、`full` (resource/subresource)、`verb`、`namespace`、`name`、`path` (lowercase non-resource URL)、`non_resource_url`、`mode`、`delegated_verb` です。Operations は `eq`、`ne`、`in`、`not_in`、`contains`、`prefix`、`suffix`、`truthy` です (`truthy` に value は不要)。`always: true` はすべてに matching します。Group、resource、subresource、verb の values は lowercase です。literal wildcard は `'*'` と記述します。wildcard grant との matching は rules 内で明示され、shell pattern expansion は行われません。

`severity_when` は、matching condition に対して別の severity を任意で選択します。`severity: delegated` は、制約された impersonation 用に予約されています。その `delegated_severities` map は、delegated action の classification を conditional rating に変換します。Description placeholders では、`{full}` や `{verb}` など、利用可能な fields を参照できます。rules は data であり、Python や shell code として評価されることはありません。

## Validation and synchronization

変更を submit する前に、PyYAML をインストールした状態で `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` を実行してください。book の pull-request workflow でも同じ validation が実行されます。

毎週月曜日に、両方の consumer repositories はこの book の現在の `master` を checkout し、4 つすべての files を validate し、SHA-256 hashes を比較して、bundled YAML files と生成済みの legacy lists を更新します。source manifest には book revision と各 file の hash が記録されます。book への無関係な変更では consumer commit は生成されません。各 workflow は manual run にも対応しています。Tests は workflow が変更された data を consumer の default branch に commit する前に実行されます。失敗した場合、その branch は変更されません。更新の間、consumers は offline で bundled copies を使用し続けます。

consumer 内で local に更新するには、`python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` を実行します。書き込みを行わずに stale copies を検出するには、`--check` を追加してください。

両方の consumers における source fetching は、bounded checkout deadlines と increasing delays を使用して 5 回 retry します。不完全な downloads は temporary directories に保持されます。retry を使い切った場合、既存の bundled data は変更されません。
