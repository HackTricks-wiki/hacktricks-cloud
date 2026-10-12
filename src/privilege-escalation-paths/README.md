# 提权路径

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud 维护供 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) 使用的机器可读提权目录。每项技术都说明主体必须实际持有哪些权限，以及这些权限适用于哪些资源，才能获得一组目标主体的权限。Blue-CloudPEASS 会根据只读清单快照离线评估这些条目，并绘制主体之间的攻击路径，同时将授予权限的策略或绑定作为证据，并指出移除该路径的缓解措施。请在此处编辑规范文件，而不是编辑使用方中的副本。

条目仅描述前置条件、可达目标和缓解措施，不包含命令、payload 或执行步骤；链接的 HackTricks 页面会介绍该技术。

## 目录结构

每个平台（`aws`、`gcp`、`azure`、`k8s`）各有一个目录，每项服务各有一个 `<service>.yaml` 文件，其中包含 YAML 技术列表。名为 `_excluded*.yaml` 的文件列出经过审核但有意不创建条目的 HackTricks 技术，例如 post-exploitation、persistence，或无法通过配置建模的技术，并说明原因。`privesc-technique.schema.json` 是导出的 JSON Schema，用于编辑器补全和验证。

## 技术字段

- `id`：全局唯一，使用小写 kebab-case，并以平台名称为前缀。
- `provider`、`service`、`title` 和 `summary`：用一句话描述源主体会获得什么。
- `source`：记录该技术的 HackTricks 页面和锚点，相对于本书的路径。`source_revision` 是所依据的本书提交。
- `requires`：源主体必须持有的权限。`all_of` 列出所有必需项，`any_of` 列出可选项。AWS 和 GCP 项使用 `action` 和 `resource`；Azure 项使用 `action`（或 `data_action`）和 `scope`；Entra ID 项使用 `entra_permission` 或 `entra_role`；Kubernetes 项使用 `verb`、`resource`、`subresource`、`api_group` 和 `namespace`。诸如 `{target.arn}` 的占位符会绑定到目标。
- `target`：目标 `kind`、一个所有条件都必须满足主体才可达的 `selector`，以及其 `scope`。
- `conditions` 和 `blockers`：说明实践中可能阻断路径的因素，例如条件键、SCP、边界或准入策略。
- `confidence`、`severity`、`mitigation`、`references` 以及可选的 `notes`。

未知字段、目标类型、选择器键和占位符都会被拒绝，而不会被忽略，因此条目不会在不知情的情况下扩大或缩小目标集合。请先在使用方评估器中支持新的选择器。

### Schema v2 关联

v2 加载器新增了两个占位符和一个 AWS 选择器，并允许 GCP 目标使用现有的 K8s 运行中 Pod 选择器。这些字段必须与已收集的清单数据进行精确关联；缺少清单数据时，覆盖情况为未知，而不是判定为可达路径。

| 字段 | 用途和必需格式 |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` 和 `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | 在 AWS `aws_account_admin` 目标上同时使用。每个权限要求备选项都必须包含对该占位符执行的 `iam:CreatePolicyVersion`。该策略必须附加到源主体可在同一账户中代入的角色；评估器会检查策略版本容量，并重新计算角色的有效权限。不覆盖 `SetDefaultPolicyVersion`。 |
| `target.selector.k8s_sa_used_by_running_pod: true` | 用于 `scope: cluster` 的 GCP `k8s_service_account` 目标，选择在匹配的 GKE 集群中被运行中 Pod 使用且有可用令牌的 KSA。不要与 `k8s_sa_in_cluster` 或 `k8s_sa_has_token_secret` 同时使用。现有 K8s 用法不变。 |
| `{source_rolebound_clusterrole}` | 在 `api_group: rbac.authorization.k8s.io` 且 `namespace: "*"` 的 K8s `clusterroles` 权限要求中，将其用作 `resource_name`。每个备选项都必须对同一名称具有 `escalate`，以及 `update` 或 `patch` 权限。目标必须是 `scope: same_namespace` 的 `k8s_service_account`，并带有 `selector.k8s_sa_in_namespace: "{target.namespace}"`；RoleBinding 必须在该命名空间中绑定源主体。 |

## 验证与同步

提交更改前，请在安装 PyYAML 后运行 `python scripts/validate_privesc_paths.py --book-root .`。该脚本会检查目录结构、使用评估器的严格加载器（`scripts/privesc_paths_schema.py`，即 Blue-CloudPEASS schema 模块的副本）检查每个条目、检查唯一 ID、源页面和标题锚点，并确认 JSON Schema 为最新版本。使用 `--peaso-root /path/to/Blue-CloudPEASS` 还可逐字节比较两个 schema 文件与使用方中的对应文件。本书的 pull-request 工作流会运行相同的验证。

每周一，Blue-CloudPEASS 会检出本书当前的 `master`，验证这些文件，并将每个文件的 SHA-256 哈希值与上次同步时记录的哈希值进行比较。上游新增、更新和删除的内容会替换使用方中未更改的副本。若文件在双方都发生更改，则会报告冲突；未经明确审核的台账记录，不会删除任何技术 ID。内容无效或测试失败时，使用方的默认分支不会发生更改。本书中的无关更改不会产生使用方提交。
{{#include ../banners/hacktricks-training.md}}
