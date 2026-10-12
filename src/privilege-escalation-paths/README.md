# 권한 상승 경로

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud는 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS)가 사용하는 기계 판독 가능한 권한 상승 카탈로그를 관리합니다. 각 기법은 주체가 특정 대상 주체의 권한을 얻기 위해 어떤 리소스에서 어떤 권한을 실질적으로 보유해야 하는지 명시합니다. Blue-CloudPEASS는 읽기 전용 인벤토리 스냅샷을 오프라인으로 분석하고, 권한을 부여하는 정책이나 바인딩을 근거로 제시하며 해당 경로를 제거하는 완화 방법과 함께 주체 간 공격 경로를 표시합니다. 소비자 쪽 복사본이 아니라 여기의 표준 파일을 수정하세요.

항목에는 사전 조건, 도달 가능한 대상 및 완화 방법만 기술합니다. 명령, 페이로드 또는 실행 단계는 포함하지 않습니다. 링크된 HackTricks 페이지에서 기법을 설명합니다.

## 레이아웃

플랫폼별로 디렉터리(`aws`, `gcp`, `azure`, `k8s`)가 하나씩 있으며, 서비스마다 `<service>.yaml` 파일 하나에 YAML 기법 목록이 들어 있습니다. `_excluded*.yaml`로 시작하는 파일에는 검토했지만 의도적으로 항목을 만들지 않은 HackTricks 기법이 이유와 함께 나열됩니다. 여기에는 post-exploitation, persistence 또는 설정만으로 모델링할 수 없는 기법 등이 포함됩니다. `privesc-technique.schema.json`은 편집기 자동 완성 및 검증에 사용하는 JSON Schema 내보내기 파일입니다.

## 기법 필드

- `id`: 플랫폼 접두사가 붙은 전역적으로 고유한 소문자 kebab-case 식별자입니다.
- `provider`, `service`, `title`, `summary`: 소스가 무엇을 얻는지 설명하는 한 문장입니다.
- `source`: 이 책을 기준으로 한, 기법을 설명하는 HackTricks 페이지 및 앵커입니다. `source_revision`은 참조한 책의 커밋입니다.
- `requires`: 소스가 보유해야 하는 권한입니다. `all_of`에는 필요한 모든 항목을, `any_of`에는 대안 항목을 나열합니다. AWS와 GCP 항목은 `action` 및 `resource`를 사용하고, Azure 항목은 `action`(또는 `data_action`) 및 `scope`를 사용하며, Entra ID 항목은 `entra_permission` 또는 `entra_role`을 사용하고, Kubernetes 항목은 `verb`, `resource`, `subresource`, `api_group`, `namespace`를 사용합니다. `{target.arn}` 같은 플레이스홀더는 요구 사항을 대상에 연결합니다.
- `target`: 대상 `kind`, 주체가 도달 가능한 대상이 되려면 모든 조건을 충족해야 하는 `selector`, 그리고 해당 대상의 `scope`입니다.
- `conditions` 및 `blockers`: 조건 키, SCP, boundaries 또는 admission policies처럼 실제 경로를 막을 수 있는 요소입니다.
- `confidence`, `severity`, `mitigation`, `references` 및 선택적 `notes`.

알 수 없는 필드, 대상 종류, selector 키 및 플레이스홀더는 무시되지 않고 거부됩니다. 따라서 항목이 대상 집합을 조용히 확대하거나 축소할 수 없습니다. 새 selector를 추가하려면 먼저 소비자 평가기에 지원을 추가하세요.

### Schema v2 조인

v2 로더는 플레이스홀더 두 개와 AWS selector 하나를 추가하며, 기존 K8s 실행 중인 pod selector를 GCP 대상에서도 사용할 수 있도록 허용합니다. 이 필드에는 수집된 인벤토리와의 정확한 조인이 필요합니다. 인벤토리가 없으면 도달 가능한 경로가 아니라 커버리지 알 수 없음으로 처리됩니다.

| 필드 | 사용법 및 필수 형식 |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` 및 `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | AWS `aws_account_admin` 대상에서 두 항목을 함께 사용하세요. 모든 권한 대안에는 해당 플레이스홀더에 대한 `iam:CreatePolicyVersion`이 포함되어야 합니다. 정책은 소스가 같은 계정에서 assume할 수 있는 역할에 연결되어야 합니다. 평가기는 정책 버전 용량을 확인하고 역할의 유효 권한을 다시 계산합니다. `SetDefaultPolicyVersion`은 지원하지 않습니다. |
| `target.selector.k8s_sa_used_by_running_pod: true` | `scope: cluster`인 GCP `k8s_service_account` 대상에서 사용하면, 일치하는 GKE 클러스터에서 사용 가능 토큰을 보유한 실행 중인 pod가 사용하는 KSA를 선택합니다. `k8s_sa_in_cluster` 또는 `k8s_sa_has_token_secret`과 함께 사용하지 마세요. 기존 K8s 사용 방식은 변경되지 않습니다. |
| `{source_rolebound_clusterrole}` | `api_group: rbac.authorization.k8s.io` 및 `namespace: "*"`인 K8s `clusterroles` 요구 사항에서 `resource_name`으로 사용합니다. 각 대안에는 같은 이름에 대한 `escalate` 및 `update` 또는 `patch`가 필요합니다. 대상은 `scope: same_namespace` 및 `selector.k8s_sa_in_namespace: "{target.namespace}"`인 `k8s_service_account`여야 합니다. RoleBinding은 해당 네임스페이스에서 소스를 바인딩해야 합니다. |

## 검증 및 동기화

변경 사항을 제출하기 전에 PyYAML을 설치하고 `python scripts/validate_privesc_paths.py --book-root .`를 실행하세요. 이 명령은 디렉터리 구조, 평가기의 엄격한 로더(`scripts/privesc_paths_schema.py`, Blue-CloudPEASS 스키마 모듈의 복사본)를 사용한 모든 항목, 고유 ID, 소스 페이지 및 heading 앵커, JSON Schema 최신 여부를 확인합니다. `--peaso-root /path/to/Blue-CloudPEASS`를 사용하면 두 스키마 파일이 소비자 쪽 파일과 바이트 단위로 일치하는지도 비교합니다. 이 책의 pull request 워크플로에서도 같은 검증을 실행합니다.

매주 월요일, Blue-CloudPEASS는 이 책의 현재 `master`를 체크아웃하고 해당 파일을 검증한 다음 각 파일의 SHA-256 해시를 이전 동기화 때 기록한 해시와 비교합니다. 업스트림에서 추가, 갱신 또는 삭제된 파일은 소비자 쪽에서 변경되지 않은 복사본을 대체합니다. 양쪽에서 모두 변경된 파일은 충돌로 보고되며, 명시적으로 검토된 ledger 없이는 기법 ID를 삭제하지 않습니다. 콘텐츠가 유효하지 않거나 테스트가 실패하면 소비자의 기본 브랜치는 변경되지 않습니다. 책의 관련 없는 변경 사항은 소비자 커밋을 만들지 않습니다.
{{#include ../banners/hacktricks-training.md}}
