# 权限风险分类

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud 维护由 [CloudPEASS](https://github.com/peass-ng/CloudPEASS) 和 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) 使用的共享权限严重性数据。请在此处编辑平台的规范文件，而不要编辑任一使用方中的生成副本。

- **严重**：可直接或几乎独立地授予强大权限、创建身份，或启用特权执行的权限。
- **高**：可访问敏感信息或凭据，或提供有条件的权限提升路径。
- **中**：DoS/中断、运营中断、常规更改，或尚未证明存在敏感数据访问或权限提升路径的有条件能力。
- **低**：常规发现和元数据访问。

每个平台有一个规范 YAML 文件：[AWS](aws.yaml)、[GCP](gcp.yaml)、[Azure](azure.yaml) 和 [Kubernetes](k8s.yaml)。这些是机器可读文件；平台页面会在浏览器中显示完整的 YAML，并说明如何编辑。内嵌查看器使用书中的副本，而 PEASS 工作流会从 GitHub 获取规范文件。

## Cloud provider files

`version` 和 `provider` 用于标识 schema。`permission_categories` 包含四个单独的权限列表。将权限移至其他列表即可更改其评级。AWS 和 Azure 的匹配不区分大小写；GCP 的匹配区分大小写。同一严重性下可以重复大小写别名，但不允许存在相互冲突的评级。

`severity_overrides` 包含经过审核的通用规则例外。如果某个例外也出现在目录中，则两处条目必须一致。`severity_caps` 用于防止权限组合提升所选权限的评级。`non_permission_identifiers` 用于排除已记录的 API 方法名称、条件键以及其他并非实际授权权限的字符串。

`combinations.critical` 和 `combinations.high` 是权限列表的列表：内层列表中的每项权限都必须被授予，该组合才适用。请保持组合完整；将其拆分成单独授权会夸大风险。目录中未包含的权限仍由现有的精确匹配和正则表达式字段作为回退规则处理。完整重写分类器或新增匹配行为仍需修改使用方代码。

## Kubernetes file

`rules` 按顺序排列：第一个匹配的规则生效。每条规则都有唯一的 `id`、一个 `match`、一个 `severity` 和一个通俗易懂的 `description`。将更具体的规则添加在更宽泛的规则之前，或更改现有规则的严重性。保留最后的无条件回退规则。

匹配条件可使用 `all`、`any` 和 `not` 进行组合，也可使用 `field`、`op` 和 `value` 进行比较。可用字段包括 `group`、`resource`、`subresource`、`full`（resource/subresource）、`verb`、`namespace`、`name`、`path`（小写的非资源 URL）、`non_resource_url`、`mode` 和 `delegated_verb`。操作包括 `eq`、`ne`、`in`、`not_in`、`contains`、`prefix`、`suffix` 和 `truthy`（不需要 value）。`always: true` 匹配所有内容。Group、resource、subresource 和 verb 的值均为小写。字面量通配符写作 `'*'`；规则中会明确匹配通配符授权，而不是进行 shell 模式展开。

`severity_when` 可为匹配的条件指定另一种严重性。`severity: delegated` 专用于受限模拟：其 `delegated_severities` 映射会将被委托操作的分类转换为条件评级。描述中的占位符可以引用可用字段，例如 `{full}` 和 `{verb}`。这些规则是数据，绝不会作为 Python 或 shell 代码执行。

## Validation and synchronization

安装 PyYAML 后，在提交更改前运行 `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only`。本书的 pull request 工作流会执行相同的验证。

每周一，两个使用方仓库都会检出本书当前的 `master`，验证全部四个文件、比较 SHA-256 哈希值，并更新其捆绑的 YAML 文件和生成的旧版列表。源清单会记录本书的修订版本以及每个文件的哈希值。对本书的无关更改不会导致使用方提交更改。每个工作流也支持手动运行。工作流将更改的数据提交到使用方的默认分支前会先运行测试；如果测试失败，该分支不会发生更改。在两次更新之间，使用方仍会继续离线使用其捆绑副本。

若要在使用方仓库中本地更新，请运行 `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`。添加 `--check` 可在不写入文件的情况下检测过期副本。

两个使用方在获取源文件时都会重试五次，并采用有上限的检出时限和逐渐增加的间隔。不完整的下载会保留在临时目录中；重试耗尽后，现有的捆绑数据保持不变。
{{#include ../banners/hacktricks-training.md}}
