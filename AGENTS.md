# AGENTS.md

이 repository에서 작업하는 future agents를 위한 guidance입니다.

## Repository Context

이는 HackTricks Cloud mdBook repository입니다. 관련 main book은 다음 위치에 있습니다.

`/Users/carlospolop/git/hacktricks`

공유 theme/search 동작에 대한 변경 사항은 두 repository 모두에 적용해야 하는 경우가 많습니다.

## Search Index Loading Contract

custom search UI는 다음 위치에 있습니다.

`theme/ht_searcher.js`

다음 위치에 generated copy가 있을 수도 있습니다.

`book/theme/ht_searcher.js`

production에서 이미 build된 `book/` directory를 deploy하는 경우, 두 copy를 모두 update하거나 deploy 전에 book을 rebuild해야 합니다.

search index source policy는 중요하며 cost-sensitive합니다.

- public hosts에서는 모든 language-specific 및 fallback candidate를 `HackTricks-wiki/hacktricks-searchindex`에서만 load합니다. 동일 origin의 mdBook output으로 fallback하지 않습니다. production에서 대규모 index를 `cloud.hacktricks.wiki`에서 serve하면 비용이 높습니다.
- localhost, `.local`/`.internal` hosts, loopback, RFC1918, carrier-grade NAT, link-local 또는 private IPv6 addresses에서는 동일 origin의 mdBook output만 load하여 local/container deployments가 self-contained 상태로 유지되도록 합니다.

이 repo에서 예상되는 local fallback은 다음과 같습니다.

`/searchindex.js`

이 repo의 main-book fallback은 다음과 같습니다.

`/searchindex-book.js`

이 local files는 private-network sources 전용입니다. public hosts는 `HackTricks-wiki/hacktricks-searchindex`의 remote `searchindex-<lang>.js.gz` 및 `searchindex-cloud-<lang>.js.gz` files만 사용해야 합니다.

## Search Index Publishing

encrypted compressed search indexes를 `HackTricks-wiki/hacktricks-searchindex`에 publish하는 workflows는 다음과 같습니다.

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

generated source file은 `book/searchindex.js`입니다. published remote artifact names는 다음과 같습니다.

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader는 compact v2 artifact를 우선 사용하며 `.js.gz` artifact를 legacy fallback으로 유지합니다. 둘 다 `theme/ht_searcher.js`에 정의된 key를 사용하는 XOR-encrypted gzip payload입니다.

loader는 lazy 상태를 유지해야 합니다. 일반적인 page navigation에서는 visitor가 search를 열거나 사용할 때까지 search worker를 생성하거나 index를 download해서는 안 됩니다. Remote compressed responses는 origin별로 24시간 동안 Cache Storage에 persist되므로 subsequent pages에서 재사용할 수 있습니다. expired entry를 refresh하지 못하는 경우 stale-cache fallback을 유지합니다.

## Build And Validation

일반적인 local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build`가 실패하면 다음을 확인합니다.

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- 검색에는 `rg`를 우선 사용합니다.
- 명시적으로 요청되지 않은 경우 generated `book/` output을 commits에 포함하지 않습니다. 이미 build된 pages를 즉시 수정해야 하는 경우에는 search loader fixes가 예외입니다.
- shared theme 동작을 변경하는 경우 `/Users/carlospolop/git/hacktricks`의 matching file을 비교하고 update합니다.
- 관련 없는 local changes를 revert하지 않습니다.
