# AGENTS.md

이 저장소에서 작업하는 향후 agents를 위한 지침입니다.

## Repository Context

이 저장소는 HackTricks Cloud mdBook repository입니다. 관련된 메인 book은 다음 위치에 있습니다:

`/Users/carlospolop/git/hacktricks`

공유 theme/search 동작에 대한 변경 사항은 두 repository 모두에 적용해야 하는 경우가 많습니다.

## Search Index Loading Contract

custom search UI는 다음 위치에 있습니다:

`theme/ht_searcher.js`

다음 위치에 생성된 copy가 있을 수도 있습니다:

`book/theme/ht_searcher.js`

production에서 이미 build된 `book/` directory를 배포하는 경우, 두 copy를 모두 업데이트하거나 배포 전에 book을 다시 build하세요.

search index source policy는 중요하며 비용에 민감합니다:

- public host에서는 모든 language-specific 및 fallback candidate를
`HackTricks-wiki/hacktricks-searchindex`에서만 load하세요. 동일 origin의 mdBook output으로 fallback하지 마세요. production에서 `cloud.hacktricks.wiki`로 large index를 제공하는 것은 비용이 많이 듭니다.
- localhost, `.local`/`.internal` host, loopback, RFC1918, carrier-grade NAT, link-local 또는 private IPv6 address에서는 동일 origin의 mdBook output만 load하여 local/container deployment가 self-contained 상태를 유지하도록 하세요. 영어가 아닌 page에서는 language-prefixed local path를 먼저 시도하고(예: `/es/searchindex.js`), root English index는 fallback으로만 사용하세요.

이 repo에서 예상되는 local fallback은 다음과 같습니다:

`/searchindex.js`

이 repo의 main-book fallback은 다음과 같습니다:

`/searchindex-book.js`

이러한 local file은 private-network source 전용입니다. public host에서는 `HackTricks-wiki/hacktricks-searchindex`의 remote `searchindex-<lang>.js.gz` 및 `searchindex-cloud-<lang>.js.gz` file만 사용해야 합니다.

## Search Index Publishing

encrypted compressed search index를
`HackTricks-wiki/hacktricks-searchindex`에 publish하는 workflow는 다음과 같습니다:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

생성되는 source file은 `book/searchindex.js`입니다. publish되는 remote artifact name은 다음과 같습니다:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader는 compact v2 artifact를 우선 사용하고 `.js.gz` artifact를 legacy fallback으로 유지합니다. 둘 다 `theme/ht_searcher.js`에 정의된 key를 사용하는 XOR-encrypted gzip payload입니다.

loader는 lazy 상태를 유지해야 합니다. 일반적인 page navigation에서는 visitor가 search를 열거나 사용할 때까지 search worker를 생성하거나 index를 download하지 않아야 합니다. Remote compressed response는 origin별로 24시간 동안 Cache Storage에 persist되므로 이후 page에서 재사용할 수 있습니다. expired entry를 refresh하지 못할 때 stale-cache fallback을 유지하세요.

## Build And Validation

일반적인 local check:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build`가 실패하면 다음을 확인하세요:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 검색에는 `rg` 사용을 우선하세요.
- 명시적으로 요청하지 않는 한 생성된 `book/` output을 commit에 포함하지 마세요. 단, 이미 build된 page를 즉시 수정해야 하는 경우에는 search loader fix가 예외입니다.
- shared theme behavior를 변경하는 경우 `/Users/carlospolop/git/hacktricks`의 해당 file을 비교하고 업데이트하세요.
- 관련 없는 local 변경 사항을 되돌리지 마세요.
