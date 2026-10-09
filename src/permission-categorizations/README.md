# Permission risk categorizations

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud는 [CloudPEASS](https://github.com/peass-ng/CloudPEASS)와 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS)가 사용하는 공유 권한 심각도 데이터를 관리합니다. 소비자 저장소의 생성된 복사본 대신 여기의 플랫폼 정본 파일을 수정하세요.

- **Critical**: 강력한 권한을 직접 또는 거의 독립적으로 부여하거나, ID를 생성하거나, 권한이 높은 실행을 가능하게 하는 권한입니다.
- **High**: 민감한 정보나 자격 증명에 접근하거나, 조건부 권한 상승 경로를 제공하는 권한입니다.
- **Medium**: DoS/Break, 운영 중단, 일반적인 변경 또는 민감한 데이터나 권한 경로가 입증되지 않은 조건부 기능에 해당합니다.
- **Low**: 일반적인 탐색 및 메타데이터 접근에 해당합니다.

플랫폼별 정본 YAML 파일은 하나씩 있습니다: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), [Kubernetes](k8s.yaml). 이 파일은 기계가 읽을 수 있는 형식이며, 플랫폼 페이지에서는 전체 YAML을 브라우저에 표시하고 편집 방법을 설명합니다. 인라인 뷰어는 책에 포함된 복사본을 사용하고, PEASS 워크플로는 GitHub에서 정본 파일을 가져옵니다.

## Cloud provider files

`version`과 `provider`는 스키마를 식별합니다. `permission_categories`에는 각 권한 목록이 들어 있습니다. 권한의 등급을 변경하려면 목록 간에 권한을 옮기세요. AWS와 Azure는 대소문자를 구분하지 않고 매칭하며, GCP는 대소문자를 구분합니다. 동일한 심각도 안에서는 대소문자 별칭이 중복될 수 있지만, 등급이 서로 다르면 거부됩니다.

`severity_overrides`에는 일반 규칙에 대한 감사된 예외가 포함됩니다. 예외가 카탈로그에도 있으면 두 항목의 값이 일치해야 합니다. `severity_caps`는 조합으로 인해 선택된 권한의 등급이 올라가는 것을 방지합니다. `non_permission_identifiers`는 문서화된 API 메서드 이름, 조건 키 및 실제 권한 부여 권한이 아닌 기타 문자열을 제외합니다.

`combinations.critical`과 `combinations.high`는 권한 목록의 목록입니다. 조합을 적용하려면 내부 목록의 모든 요소가 부여되어야 합니다. 조합은 하나로 유지하세요. 각 요소를 개별 권한으로 나누면 위험을 실제보다 높게 평가하게 됩니다. 카탈로그에 없는 권한에는 기존의 정확 일치 및 정규식 필드가 대체 규칙으로 적용됩니다. 전체 분류기를 다시 작성하거나 새로운 매칭 동작을 추가하려면 소비자 코드도 변경해야 합니다.

## Kubernetes file

`rules`는 순서가 중요하며, 처음으로 일치하는 규칙이 적용됩니다. 각 규칙에는 고유한 `id`, `match`, `severity`, 그리고 일반 언어로 작성된 `description`이 있습니다. 더 구체적인 규칙을 더 포괄적인 규칙보다 앞에 추가하거나 기존 규칙의 심각도를 변경하세요. 마지막의 무조건적 대체 규칙은 그대로 유지하세요.

매칭 조건은 조합에 `all`, `any`, `not`을 사용하거나, 비교에 `field`, `op`, `value`를 사용합니다. 사용할 수 있는 필드는 `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (소문자로 된 non-resource URL), `non_resource_url`, `mode`, `delegated_verb`입니다. 연산자는 `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, `truthy`입니다 (`truthy`에는 값이 필요하지 않습니다). `always: true`는 모든 항목에 일치합니다. 그룹, 리소스, 하위 리소스, verb 값은 소문자입니다. 리터럴 와일드카드는 `'*'`로 작성합니다. 와일드카드 권한 부여와의 매칭은 셸 패턴 확장이 아니라 규칙에 명시적으로 지정합니다.

`severity_when`은 일치 조건에 따라 다른 심각도를 선택할 수 있습니다. `severity: delegated`는 제한된 impersonation에만 사용되며, `delegated_severities` 맵은 위임된 작업의 분류를 조건부 등급으로 변환합니다. 설명의 자리 표시자는 `{full}`, `{verb}`처럼 사용 가능한 필드를 참조할 수 있습니다. 규칙은 데이터이며 Python이나 셸 코드로 실행되지 않습니다.

## Validation and synchronization

변경 사항을 제출하기 전에 PyYAML을 설치하고 `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only`를 실행하세요. 책의 pull-request 워크플로에서도 동일한 검증을 수행합니다.

매주 월요일 두 소비자 저장소는 이 책의 최신 `master`를 체크아웃하고, 네 파일을 모두 검증하고, SHA-256 해시를 비교한 다음, 번들 YAML 파일과 생성된 레거시 목록을 업데이트합니다. 소스 매니페스트에는 책의 리비전과 각 파일의 해시가 기록됩니다. 책의 관련 없는 변경으로는 소비자 저장소에 커밋이 생성되지 않습니다. 각 워크플로는 수동 실행도 지원합니다. 워크플로는 변경된 데이터를 소비자 저장소의 기본 브랜치에 커밋하기 전에 테스트를 실행하며, 실패하면 해당 브랜치는 변경되지 않습니다. 업데이트 사이에 소비자는 오프라인 상태에서도 번들 복사본을 계속 사용합니다.

소비자 저장소에서 로컬로 업데이트하려면 `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`를 실행하세요. 쓰기 없이 오래된 복사본을 감지하려면 `--check`를 추가하세요.

두 소비자 저장소의 소스 가져오기는 제한된 체크아웃 시간과 점점 늘어나는 대기 시간을 적용해 최대 다섯 번 재시도합니다. 다운로드가 완료되지 않으면 임시 디렉터리에 그대로 남으며, 재시도를 모두 소진해도 기존 번들 데이터는 변경되지 않습니다.
{{#include ../banners/hacktricks-training.md}}
