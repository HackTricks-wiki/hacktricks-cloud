# AGENTS.md

이 저장소에서 작업하는 향후 agents를 위한 지침입니다.

## Repository Context

이 저장소는 HackTricks Cloud mdBook repository입니다. 관련된 main book은 다음 위치에 있습니다.

`/Users/carlospolop/git/hacktricks`

공유 theme/search 동작에 대한 변경 사항은 두 repository에 모두 적용해야 하는 경우가 많습니다.

## Search Index Loading Contract

custom search UI는 다음 파일에 있습니다.

`theme/ht_searcher.js`

다음 위치에 generated copy가 있을 수도 있습니다.

`book/theme/ht_searcher.js`

production에서 이미 build된 `book/` directory를 배포하는 경우, 두 copy를 모두 업데이트하거나 배포 전에 book을 다시 build하세요.

search index loading order는 중요하며 cost-sensitive합니다.

1. GitHub repository에서 모든 language-specific 및 fallback search index를 load합니다:
`HackTricks-wiki/hacktricks-searchindex`
2. GitHub-hosted candidate가 모두 실패한 경우에만 same-origin mdBook output으로 fallback합니다.

`searchindex-cloud-en.js.gz`와 같은 GitHub-hosted fallback보다 local `/searchindex.js` fallback을 먼저 배치하지 마세요. production의 `cloud.hacktricks.wiki`에서 `searchindex.js`를 제공하는 것은 비용이 많이 듭니다.

이 repo에서 예상되는 local fallback은 다음과 같습니다.

`/searchindex.js`

이 repo의 main-book fallback은 다음과 같습니다.

`/searchindex-book.js`

이 파일은 fallback일 뿐입니다. primary source는 `HackTricks-wiki/hacktricks-searchindex`의 remote
`searchindex-<lang>.js.gz` 및 `searchindex-cloud-<lang>.js.gz` 파일로 유지해야 합니다.

## Search Index Publishing

encrypted compressed search index를
`HackTricks-wiki/hacktricks-searchindex`에 publish하는 workflows는 다음과 같습니다.

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

generated source file은 `book/searchindex.js`입니다. published remote artifact names는 다음과 같습니다.

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader는 compact v2 artifact를 우선 사용하며 `.js.gz` artifact를 legacy
fallback으로 유지합니다. 둘 다 `theme/ht_searcher.js`에 정의된 key를 사용하는 XOR-encrypted gzip payload입니다.

## Build And Validation

일반적인 local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build`가 실패하면 다음을 확인하세요.

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 검색에는 `rg` 사용을 권장합니다.
- 명시적으로 요청되지 않는 한 generated `book/` output은 commits에 포함하지 마세요. 이미 build된 pages를 즉시 수정해야 하는 경우에는 search loader fixes가 예외입니다.
- shared theme 동작을 변경하는 경우
`/Users/carlospolop/git/hacktricks`의 대응 파일을 비교하고 업데이트하세요.
- 관련 없는 local changes를 되돌리지 마세요.
