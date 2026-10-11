# 권한 상승 경로

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud는 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS)가 사용하는 machine-readable 권한 상승 카탈로그를 관리합니다. 각 technique에는 principal이 target principal 집합의 권한을 얻기 위해 실질적으로 보유해야 하는 권한과 해당 권한이 적용되는 리소스가 명시되어 있습니다. Blue-CloudPEASS는 read-only inventory snapshot을 대상으로 오프라인에서 항목을 평가하고, 권한을 부여하는 policy 또는 binding을 근거로 principal 간 공격 경로를 표시하며, 경로를 제거하는 완화 방법도 제시합니다. consumer의 사본이 아니라 이곳의 정식 파일을 수정하세요.

항목에는 사전 조건, 도달 가능한 target, 완화 방법만 기술합니다. 명령어, payload 또는 실행 단계는 포함하지 않습니다. 링크된 HackTricks 페이지에서 technique을 설명합니다.

## Layout

플랫폼별(`aws`, `gcp`, `azure`, `k8s`)로 디렉터리가 하나씩 있으며, 각 디렉터리에는 service별 `<service>.yaml` 파일이 하나씩 있습니다. 각 파일에는 technique 목록이 YAML 형식으로 들어 있습니다. `_excluded*.yaml`이라는 이름의 파일에는 post-exploitation, persistence, 또는 configuration만으로 모델링할 수 없는 technique처럼 의도적으로 항목을 만들지 않은 HackTricks technique과 그 사유가 기록되어 있습니다. `privesc-technique.schema.json`은 editor 자동 완성 및 검증에 사용하는 JSON Schema 내보내기 파일입니다.

## Technique fields

- `id`: 전역적으로 고유한 값으로, 소문자 kebab-case이며 플랫폼 접두사가 붙습니다.
- `provider`, `service`, `title`, `summary`: source가 얻는 것을 설명하는 한 문장입니다.
- `source`: technique을 설명하는 HackTricks 페이지 및 anchor이며, 이 책을 기준으로 한 상대 경로입니다. `source_revision`은 읽은 책의 commit입니다.
- `requires`: source가 보유해야 하는 권한입니다. `all_of`에는 모든 필수 항목이 나열되고, `any_of`에는 대안이 나열됩니다. AWS 및 GCP 항목은 `action`과 `resource`를 사용하고, Azure 항목은 `action`(또는 `data_action`)과 `scope`를 사용하며, Entra ID 항목은 `entra_permission` 또는 `entra_role`을 사용하고, Kubernetes 항목은 `verb`, `resource`, `subresource`, `api_group`, `namespace`를 사용합니다. `{target.arn}`과 같은 placeholder는 요구 사항을 target에 연결합니다.
- `target`: target의 `kind`, principal에 도달할 수 있으려면 조건을 모두 충족해야 하는 `selector`, 그리고 `scope`입니다.
- `conditions` 및 `blockers`: condition key, SCP, boundary 또는 admission policy 등 실제로 경로를 차단할 수 있는 요소입니다.
- `confidence`, `severity`, `mitigation`, `references` 및 선택적 `notes`.

알 수 없는 필드, target kind, selector key 및 placeholder는 무시되지 않고 거부됩니다. 따라서 항목의 target 집합이 조용히 확장되거나 축소될 수 없습니다. 새 selector는 먼저 consumer evaluator에 지원 기능을 추가하세요.

## Validation and synchronization

PyYAML을 설치한 뒤 변경 사항을 제출하기 전에 `python scripts/validate_privesc_paths.py --book-root .`를 실행하세요. 이 명령은 디렉터리 구조, evaluator의 strict loader(`scripts/privesc_paths_schema.py`, Blue-CloudPEASS schema module의 사본)를 사용한 모든 항목, 고유한 id, 이 책에 `source` 페이지가 존재하는지 여부, JSON Schema가 최신인지 여부를 검사합니다. 이 책의 pull-request workflow도 동일한 검증을 실행합니다.

매주 월요일, Blue-CloudPEASS는 이 책의 최신 `master`를 checkout하고 이 파일들을 검증한 다음, 각 파일의 SHA-256 hash를 이전 동기화 때 기록한 hash와 비교합니다. upstream에서 추가, 수정 또는 삭제된 내용은 consumer에서 변경되지 않은 사본을 대체합니다. 양쪽에서 모두 변경된 파일은 conflict로 보고되며, 명시적으로 검토된 ledger 없이는 technique id가 삭제되지 않습니다. 콘텐츠가 유효하지 않거나 테스트가 실패하면 consumer의 default branch는 변경되지 않습니다. 책에서 관련 없는 변경이 발생해도 consumer commit은 만들어지지 않습니다.

{{#include ../banners/hacktricks-training.md}}
