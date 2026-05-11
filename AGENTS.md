# AGENTS.md

이 리포지토리에서 작업하는 미래의 에이전트들을 위한 지침입니다.

## Repository Context

이것은 HackTricks Cloud mdBook 리포지토리입니다. 관련된 메인 book은 다음에 있습니다:

`/Users/carlospolop/git/hacktricks`

공유 theme/search 동작에 대한 변경은 종종 두 리포지토리 모두에 적용해야 합니다.

## Search Index Loading Contract

커스텀 search UI는 다음에 있습니다:

`theme/ht_searcher.js`

생성된 복사본이 다음에 있을 수도 있습니다:

`book/theme/ht_searcher.js`

production이 이미 빌드된 `book/` 디렉터리를 배포한다면, 두 복사본을 모두 업데이트하거나 배포 전에 book을 다시 빌드하세요.

search index 로딩 순서는 중요하며 비용에 민감합니다:

1. GitHub repository에서 모든 language-specific 및 fallback search index를 로드합니다:
`HackTricks-wiki/hacktricks-searchindex`
2. GitHub-hosted 후보들이 모두 실패한 경우에만, 같은 origin의 mdBook output으로 fallback합니다.

`searchindex-cloud-en.js.gz` 같은 GitHub-hosted fallback보다 로컬 `/searchindex.js` fallback을 먼저 두지 마세요. production의 `cloud.hacktricks.wiki`에서 `searchindex.js`를 제공하는 것은 비용이 많이 듭니다.

이 리포지토리에서 기대되는 local fallback은:

`/searchindex.js`

이 리포지토리의 main-book fallback은:

`/searchindex-book.js`

그 파일은 fallback일 뿐입니다. primary source는 `HackTricks-wiki/hacktricks-searchindex`에 있는 원격
`searchindex-<lang>.js.gz` 및 `searchindex-cloud-<lang>.js.gz` 파일로 유지되어야 합니다.

## Search Index Publishing

`HackTricks-wiki/hacktricks-searchindex`에 암호화된 압축 search index를 publish하는 workflow는 다음과 같습니다:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

생성되는 source 파일은 `book/searchindex.js`입니다. publish되는 원격 artifact 이름은 다음과 같습니다:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader는 `theme/ht_searcher.js`에 정의된 key를 사용하는 XOR-encrypted gzip payload인 원격 `.js.gz` 파일을 기대합니다.

## Build And Validation

일반적인 local check는 다음과 같습니다:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build`가 실패하면 다음을 확인하세요:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 검색에는 가능하면 `rg`를 사용하세요.
- 명시적으로 요청되지 않는 한 생성된 `book/` output은 commit에 포함하지 마세요. 이미 빌드된 페이지를 즉시 수정해야 하는 경우에는 search loader fix가 예외입니다.
- shared theme behavior를 변경한다면, `/Users/carlospolop/git/hacktricks`에 있는 매칭 파일도 비교하고 업데이트하세요.
- 관련 없는 local 변경사항을 되돌리지 마세요.
