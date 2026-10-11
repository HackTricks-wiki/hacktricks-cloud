# 权限提升路径

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud 维护机器可读的权限提升目录，[Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) 会使用该目录。每项技术都说明主体必须实际具备哪些权限，以及这些权限必须作用于哪些资源，才能获得一组目标主体的权限。Blue-CloudPEASS 会基于只读清单快照离线评估这些条目，并绘制主体之间的攻击路径，同时以授予权限的策略或绑定作为证据，并指出可移除该路径的缓解措施。请在此处编辑规范文件，而不要修改使用方中的副本。

条目只描述前提条件、可达目标和缓解措施，不包含命令、payload 或执行步骤；链接的 HackTricks 页面会说明相关技术。

## 目录结构

每个平台（`aws`、`gcp`、`azure`、`k8s`）各有一个目录，每项服务各有一个 `<service>.yaml` 文件，其中包含技术列表。名为 `_excluded*.yaml` 的文件列出已审查但有意不收录的 HackTricks 技术，例如后渗透、持久化，或无法根据配置建模的技术，并说明原因。`privesc-technique.schema.json` 是导出的 JSON Schema，可用于编辑器补全和验证。

## 技术字段

- `id`：全局唯一，使用小写 kebab-case 格式，并以平台名称为前缀。
- `provider`、`service`、`title` 和 `summary`：用一句话描述该来源能获得什么。
- `source`：记录该技术的 HackTricks 页面和锚点，相对于本书的路径。`source_revision` 是所依据的书籍提交版本。
- `requires`：来源必须具备的权限。`all_of` 列出所有必需项，`any_of` 列出可选项。AWS 和 GCP 项使用 `action` 和 `resource`，Azure 项使用 `action`（或 `data_action`）和 `scope`，Entra ID 项使用 `entra_permission` 或 `entra_role`，Kubernetes 项使用 `verb`、`resource`、`subresource`、`api_group` 和 `namespace`。`{target.arn}` 等占位符会将要求绑定到目标。
- `target`：目标 `kind`、一个 `selector`（其所有条件都必须满足，主体才可被访问）以及目标的 `scope`。
- `conditions` 和 `blockers`：实践中可能阻止该路径的因素，例如条件键、SCP、边界或准入策略。
- `confidence`、`severity`、`mitigation`、`references` 和可选的 `notes`。

未知字段、目标类型、选择器键和占位符都会被拒绝，而不会被忽略，因此条目不会在不知情的情况下扩大或缩小目标范围。请先在使用方评估器中支持新的选择器。

## 验证与同步

提交更改前，请在安装 PyYAML 后运行 `python scripts/validate_privesc_paths.py --book-root .`。该脚本会检查目录结构，使用评估器的严格加载器（`scripts/privesc_paths_schema.py`，即 Blue-CloudPEASS schema 模块的副本）验证每个条目，检查 ID 是否唯一、每个 `source` 页面是否存在于本书中，以及 JSON Schema 是否为最新版本。本书的 pull request 工作流也会运行同样的验证。

每周一，Blue-CloudPEASS 会检出本书当前的 `master`，验证这些文件，并将每个文件的 SHA-256 哈希值与上次同步时记录的哈希值进行比较。上游新增、更新和删除的内容会替换使用方中未更改的副本。如果文件在双方都有更改，则会报告冲突；未经明确审查的记录，不会删除任何技术 ID。如果内容无效或测试失败，使用方的默认分支将保持不变。对本书的无关更改不会产生使用方提交。

{{#include ../banners/hacktricks-training.md}}
