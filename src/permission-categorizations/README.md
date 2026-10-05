# 权限风险分类

HackTricks Cloud 维护由 [CloudPEASS](https://github.com/peass-ng/CloudPEASS) 和 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) 使用的共享权限严重性数据。请在此处编辑规范 platform 文件，而不是编辑任一使用方中的生成副本。

- **Critical**：直接或几乎独立地授予强大权限、创建身份或启用特权执行的权限。
- **High**：访问敏感信息、凭据或有条件的权限提升路径。
- **Medium**：DoS/Break、运行中断、普通更改，或不具备已证明的敏感数据或权限路径的条件能力。
- **Low**：普通发现和元数据访问。

每个平台有一个规范 YAML 文件：[AWS](aws.yaml)、[GCP](gcp.yaml)、[Azure](azure.yaml) 和 [Kubernetes](k8s.yaml)。这些是机器可读文件；platform 页面会在浏览器中显示其完整 YAML，并说明如何编辑。内联查看器使用 book 中的副本，而 PEASS workflows 从 GitHub 获取规范文件。

## Cloud provider 文件

`version` 和 `provider` 用于标识 schema。`permission_categories` 包含四个独立的权限列表。在列表之间移动权限即可更改其评级。AWS 和 Azure 的匹配会忽略大小写；GCP 的匹配会保留大小写。同一严重性中可以重复大小写别名，但不接受冲突的评级。

`severity_overrides` 包含经过审计的通用规则例外。如果某个例外同时出现在 catalog 中，则两条记录必须一致。`severity_caps` 防止某种组合提升所选权限的评级。`non_permission_identifiers` 排除已记录的 API-method 名称、条件键以及其他并非实际授权权限的字符串。

`combinations.critical` 和 `combinations.high` 是权限列表的列表：内部列表中的每个元素都必须被授予，该组合才会生效。请保持组合完整；将其拆分为单独的授权会夸大风险。现有的精确匹配和 regular-expression 字段仍会作为 catalog 中不存在的权限的 fallback。完整的 classifier 重写或新增 matching 行为仍需要修改 consumers 中的代码。

## Kubernetes 文件

`rules` 具有顺序：第一个匹配的 rule 获胜。每个 rule 都有唯一的 `id`、`match`、`severity` 和纯语言 `description`。请将更具体的 rule 放在更宽泛的 rule 之前，或更改现有 rule 的 severity。保留最后的无条件 fallback。

匹配使用 `all`、`any` 和 `not` 进行组合，或使用 `field`、`op` 和 `value` 进行比较。可用字段包括 `group`、`resource`、`subresource`、`full`（resource/subresource）、`verb`、`namespace`、`name`、`path`（小写的 non-resource URL）、`non_resource_url`、`mode` 和 `delegated_verb`。操作包括 `eq`、`ne`、`in`、`not_in`、`contains`、`prefix`、`suffix` 和 `truthy`（无需 value）。`always: true` 会匹配所有内容。Group、resource、subresource 和 verb 值均为小写。字面量 wildcard 写作 `'*'`；对 wildcard grant 的匹配在 rules 中显式指定，而不是进行 shell pattern expansion。

`severity_when` 可选择在满足匹配条件时使用其他 severity。`severity: delegated` 专用于受约束的 impersonation：其 `delegated_severities` map 会将 delegated action 的 classification 转换为 conditional rating。Description placeholders 可以引用可用字段，例如 `{full}` 和 `{verb}`。这些 rules 是数据，不会被作为 Python 或 shell code 求值。

## 验证和同步

提交更改前，在安装 PyYAML 的环境中运行 `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only`。book 的 pull-request workflow 会运行相同的验证。

每周一，两个 consumer repositories 都会 checkout 本 book 当前的 `master`，验证全部四个文件、比较 SHA-256 hashes，并更新其 bundled YAML files 和生成的 legacy lists。source manifest 会记录 book revision 以及每个文件的 hash。对 book 的无关更改不会产生 consumer commit。每个 workflow 也支持手动运行。Tests 会在 workflow 将更改后的数据提交到 consumer 的 default branch 之前运行；失败时该 branch 保持不变。在两次更新之间，consumers 会继续离线使用其 bundled copies。

要在 consumer 中本地更新，请运行 `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`。添加 `--check` 可检测过期副本而不写入更改。

两个 consumers 中的 source fetching 会重试五次，并使用有上限的 checkout deadlines 和逐步增加的 delays。不完整的 downloads 会保留在临时目录中；重试耗尽后，现有的 bundled data 保持不变。
