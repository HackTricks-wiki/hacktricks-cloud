# Permission 위험 분류

HackTricks Cloud는 [CloudPEASS](https://github.com/peass-ng/CloudPEASS) 및 [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS)가 사용하는 공유 permission severity 데이터를 관리합니다. 두 consumer의 생성된 복사본이 아니라 여기의 canonical platform 파일을 편집하세요.

- **Critical**: 강력한 권한을 직접 또는 거의 독립적으로 부여하거나, identity를 생성하거나, privileged execution을 가능하게 하는 permissions.
- **High**: 민감한 정보 또는 credentials에 대한 access, 혹은 조건부 privilege escalation 경로.
- **Medium**: DoS/Break, 운영 중단, 일반적인 변경 또는 민감한 데이터나 privilege 경로가 입증되지 않은 조건부 capabilities.
- **Low**: 일반적인 discovery 및 metadata access.

플랫폼별 canonical YAML 파일은 하나씩 존재합니다: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), [Kubernetes](k8s.yaml). 이 파일들은 machine-readable 파일이며, platform 페이지에서는 브라우저에 전체 YAML을 표시하고 편집 방법을 설명합니다. inline viewer는 book의 복사본을 사용하고, PEASS workflows는 GitHub에서 canonical 파일을 가져옵니다.

## Cloud provider files

`version`과 `provider`는 schema를 식별합니다. `permission_categories`에는 네 개의 개별 permission 목록이 들어 있습니다. permission을 목록 간에 이동하면 해당 rating이 변경됩니다. AWS와 Azure의 matching은 대소문자를 무시하고, GCP matching은 대소문자를 유지합니다. 대소문자 aliases는 동일한 severity 내에서 반복될 수 있지만, 서로 충돌하는 ratings는 거부됩니다.

`severity_overrides`에는 generic rules에 대한 감사된 예외가 포함됩니다. 예외가 catalog에도 나타나는 경우 두 항목은 일치해야 합니다. `severity_caps`는 특정 permissions의 조합이 더 높은 등급으로 승격되는 것을 방지합니다. `non_permission_identifiers`는 문서화된 API-method names, condition keys 및 실제 authorization permissions가 아닌 기타 문자열을 제외합니다.

`combinations.critical`과 `combinations.high`는 permission 목록의 목록입니다. 조합이 적용되려면 내부 목록의 모든 요소가 부여되어야 합니다. combinations는 함께 유지하세요. 이를 개별 grants로 분할하면 risk가 과대평가됩니다. 기존의 exact 및 regular-expression fields는 catalog에 없는 permissions에 대한 fallback으로 계속 사용됩니다. 전체 classifier rewrite 또는 새로운 matching behavior에는 여전히 consumers의 code changes가 필요합니다.

## Kubernetes file

`rules`는 순서가 있습니다. 처음으로 일치하는 rule이 적용됩니다. 각 rule에는 고유한 `id`, `match`, `severity`, plain-language `description`이 있습니다. 더 구체적인 rule은 더 광범위한 rule보다 앞에 추가하거나, 기존 rule의 severity를 변경하세요. 마지막 unconditional fallback은 유지하세요.

Matches는 `all`, `any`, `not`을 사용한 composition 또는 `field`, `op`, `value` comparison을 사용합니다. 사용 가능한 fields는 `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (소문자 non-resource URL), `non_resource_url`, `mode`, `delegated_verb`입니다. Operations는 `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, `truthy`이며, `truthy`에는 value가 필요하지 않습니다. `always: true`는 모든 항목과 일치합니다. Group, resource, subresource, verb 값은 소문자입니다. literal wildcard는 `'*'`로 작성합니다. wildcard grant와의 matching은 shell pattern expansion이 아니라 rules에서 명시적으로 처리됩니다.

`severity_when`은 matching condition에 대해 다른 severity를 선택적으로 적용합니다. `severity: delegated`는 constrained impersonation을 위해 예약되어 있으며, 해당 항목의 `delegated_severities` map은 delegated action의 classification을 conditional rating으로 변환합니다. Description placeholders는 `{full}`, `{verb}`와 같이 사용 가능한 fields를 참조할 수 있습니다. Rules는 data이며 Python 또는 shell code로 평가되지 않습니다.

## Validation and synchronization

변경 사항을 제출하기 전에 PyYAML이 설치된 상태에서 `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only`를 실행하세요. Book의 pull-request workflow도 동일한 validation을 실행합니다.

매주 월요일 두 consumer repositories는 이 book의 현재 `master`를 checkout하고, 네 파일 모두를 validate하며, SHA-256 hashes를 비교한 후 bundled YAML files와 generated legacy lists를 업데이트합니다. Source manifest에는 book revision과 각 파일의 hash가 기록됩니다. book의 관련 없는 변경으로는 consumer commit이 생성되지 않습니다. 각 workflow는 manual run도 지원합니다. Tests는 workflow가 변경된 data를 consumer의 default branch에 commit하기 전에 실행되며, 실패하면 해당 branch는 변경되지 않습니다. Consumers는 업데이트 사이에 offline 상태에서도 bundled copies를 계속 사용합니다.

Consumer에서 로컬로 업데이트하려면 `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`를 실행하세요. 파일을 쓰지 않고 오래된 copies를 감지하려면 `--check`를 추가하세요.

두 consumers의 source fetching은 제한된 checkout deadlines와 점점 증가하는 delays를 적용하여 다섯 번 재시도합니다. 불완전한 downloads는 temporary directories에 유지되며, 모든 재시도가 소진되면 기존 bundled data는 변경되지 않습니다.
