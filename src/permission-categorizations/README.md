# 权限风险分类

HackTricks Cloud 维护由 [CloudPEASS](https://github.com/peass-ng/CloudPEASS) 和 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) 使用的共享权限严重性数据。请在此处编辑规范平台文件，而不是编辑任一 consumer 中生成的副本。

- **Critical**：直接或几乎独立地授予强大权限、创建身份或启用特权执行的权限。
- **High**：可访问敏感信息、凭据，或可利用有条件的权限提升路径。
- **Medium**：DoS/Break、运行中断、普通更改，或没有已证明的敏感数据或权限路径的有条件能力。
- **Low**：普通发现和元数据访问。

每个平台都有一个规范 YAML 文件：[AWS](aws.yaml)、[GCP](gcp.yaml)、[Azure](azure.yaml) 和 [Kubernetes](k8s.yaml)。这些是机器可读文件，平台页面说明了如何编辑它们。

## Cloud provider 文件

`version` 和 `provider` 用于标识 schema。`permission_categories` 包含四个独立的权限列表。将权限从一个列表移动到另一个列表即可更改其评级。AWS 和 Azure 的匹配会忽略大小写；GCP 的匹配会保留大小写。同一严重性中可以重复大小写别名，但冲突的评级会被拒绝。

`severity_overrides` 包含经过审计的通用规则例外。如果某个例外也出现在 catalog 中，则两条记录必须一致。`severity_caps` 可阻止某种组合提升选定权限的评级。`non_permission_identifiers` 会排除已记录的 API-method 名称、condition key 以及其他并非实际 authorization permission 的字符串。

`combinations.critical` 和 `combinations.high` 是权限列表的列表：内部列表中的每个元素都必须被授予，该组合才会生效。请保持组合完整；将其拆分为单独的授予项会夸大风险。现有的 exact 和 regular-expression 字段仍作为 catalog 中不存在的权限的 fallback。完整的 classifier 重写或新增匹配行为仍需要修改 consumer 中的代码。

## Kubernetes 文件

`rules` 按顺序排列：第一个匹配的规则优先。每条规则都有唯一的 `id`、`match`、`severity` 和普通语言的 `description`。请将更具体的规则放在更宽泛的规则之前，或更改现有规则的严重性。保留最后的无条件 fallback。

匹配可以使用 `all`、`any` 和 `not` 进行组合，也可以使用 `field`、`op` 和 `value` 进行比较。可用字段包括 `group`、`resource`、`subresource`、`full`（resource/subresource）、`verb`、`namespace`、`name`、`path`（小写的 non-resource URL）、`non_resource_url`、`mode` 和 `delegated_verb`。可用操作包括 `eq`、`ne`、`in`、`not_in`、`contains`、`prefix`、`suffix` 和 `truthy`（不需要 value）。`always: true` 会匹配所有内容。Group、resource、subresource 和 verb 的值均为小写。字面量 wildcard 写作 `'*'`；匹配 wildcard grant 是规则中的显式行为，而不是 shell pattern expansion。

`severity_when` 可根据匹配条件选择另一种严重性。`severity: delegated` 专用于受限 impersonation：其 `delegated_severities` map 会将 delegated action 的分类转换为 conditional rating。Description placeholder 可以引用可用字段，例如 `{full}` 和 `{verb}`。这些规则是数据，绝不会作为 Python 或 shell 代码执行。

## 验证和同步

在提交更改前，请在安装 PyYAML 的环境中运行 `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only`。本书的 pull-request workflow 会运行相同的验证。

每周一，两个 consumer repository 都会 checkout 本书当前的 `master`，验证全部四个文件、比较 SHA-256 hash，并更新其 bundled YAML 文件和生成的 legacy list。source manifest 会记录本书的 revision 以及每个文件的 hash。对本书进行无关更改不会产生 consumer commit。每个 workflow 也支持手动运行。Tests 会在 workflow 将更改后的数据提交到 consumer 的 default branch 之前运行；失败时该 branch 保持不变。在更新之间，consumer 会继续离线使用其 bundled copy。

要在 consumer 中本地更新，请运行 `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`。添加 `--check` 可检测过期副本而不写入它们。
