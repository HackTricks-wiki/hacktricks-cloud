# AGENTS.md

Riglyne vir toekomstige agents wat in hierdie repository werk.

## Repository Context

Dit is die HackTricks Cloud mdBook-repository. Die verwante hoofboek is geleë by:

`/Users/carlospolop/git/hacktricks`

Veranderinge aan gedeelde theme/search-gedrag moet dikwels in albei repositories toegepas word.

## Search Index Loading Contract

Die custom search UI is geleë in:

`theme/ht_searcher.js`

Daar kan ook 'n gegenereerde kopie wees by:

`book/theme/ht_searcher.js`

Indien production die reeds geboude `book/`-directory deploy, dateer albei kopieë op of rebuild die
book voor deployment.

Die volgorde waarin die search index gelaai word, is belangrik en cost-sensitive:

1. Laai elke language-specific en fallback search index vanaf die GitHub-repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Slegs indien alle GitHub-hosted kandidate misluk, val terug na dieselfde-origin mdBook-output.

Moenie die plaaslike `/searchindex.js`-fallback voor enige GitHub-hosted fallback, soos
`searchindex-cloud-en.js.gz`, plaas nie. Die serving van `searchindex.js` vanaf
`cloud.hacktricks.wiki` in production is duur.

Vir hierdie repo is die verwagte plaaslike fallback:

`/searchindex.js`

Die main-book-fallback vir hierdie repo is:

`/searchindex-book.js`

Daardie file is slegs 'n fallback. Die primary source moet die remote
`searchindex-<lang>.js.gz`- en `searchindex-cloud-<lang>.js.gz`-files in
`HackTricks-wiki/hacktricks-searchindex` bly.

## Search Index Publishing

Die workflows wat encrypted compressed search indexes na `HackTricks-wiki/hacktricks-searchindex` publish, is:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die gegenereerde source file is `book/searchindex.js`. Die gepubliseerde remote artifact-name is:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Die browser loader verkies die compact v2-artifact en behou die `.js.gz`-artifact as 'n legacy
fallback. Albei is XOR-encrypted gzip-payloads wat die sleutel gebruik wat in
`theme/ht_searcher.js` gedefinieer is.

Die loader moet lazy bly: normale page navigation moet nie die search worker skep of 'n index
download voordat die besoeker search oopmaak of gebruik nie. Remote compressed responses word vir
24 uur per origin in Cache Storage persist sodat daaropvolgende pages dit kan hergebruik. Behou die
stale-cache-fallback wanneer die refresh van 'n expired entry misluk.

## Build And Validation

Algemene plaaslike checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Indien `mdbook build` misluk, check:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Verkies `rg` vir searching.
- Hou gegenereerde `book/`-output uit commits, tensy dit uitdruklik versoek word. Search loader-fixes
is 'n uitsondering wanneer die reeds-geboude pages onmiddellik reggestel moet word.
- Indien shared theme-gedrag verander word, vergelyk en dateer die ooreenstemmende file in
`/Users/carlospolop/git/hacktricks` op.
- Moenie onverwante plaaslike veranderinge revert nie.
