# AGENTS.md

Riglyne vir toekomstige agents wat in hierdie repository werk.

## Repository-konteks

Dit is die HackTricks Cloud mdBook-repository. Die verwante hoofboek is geleë by:

`/Users/carlospolop/git/hacktricks`

Veranderinge aan gedeelde theme-/search-gedrag moet dikwels in albei repositories toegepas word.

## Kontrak vir die laai van die search-index

Die pasgemaakte search-UI is geleë in:

`theme/ht_searcher.js`

Daar kan ook 'n gegenereerde kopie by wees:

`book/theme/ht_searcher.js`

As production die reeds geboude `book/`-directory ontplooi, werk albei kopieë by of bou die boek voordat dit ontplooi word.

Die laai-orde van die search-index is belangrik en kostesensitief:

1. Laai elke taalspesifieke en fallback-search-index vanaf die GitHub-repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Slegs as al die GitHub-gehoste kandidate misluk, val terug na dieselfde-oorsprong mdBook-output.

Moenie die plaaslike `/searchindex.js`-fallback voor enige GitHub-gehoste fallback, soos `searchindex-cloud-en.js.gz`, plaas nie. Om `searchindex.js` vanaf `cloud.hacktricks.wiki` in production te bedien, is duur.

Vir hierdie repo is die verwagte plaaslike fallback:

`/searchindex.js`

Die hoofboek se fallback vir hierdie repo is:

`/searchindex-book.js`

Daardie lêer is slegs 'n fallback. Die primêre bron moet die afgeleë
`searchindex-<lang>.js.gz`- en `searchindex-cloud-<lang>.js.gz`-lêers in
`HackTricks-wiki/hacktricks-searchindex` bly.

## Publisering van die search-index

Die workflows wat geënkripteerde, saamgeperste search-indexes na `HackTricks-wiki/hacktricks-searchindex` publiseer, is:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die gegenereerde bronlêer is `book/searchindex.js`. Die gepubliseerde afgeleë artefakname is:

- `searchindex-cloud-v2-en.json.gz` (voorkeur-kompakte index)
- `searchindex-cloud-v2-<lang>.json.gz` (voorkeur-kompakte index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Die browser-loader verkies die kompakte v2-artefak en behou die `.js.gz`-artefak as 'n legacy-fallback. Albei is XOR-geënkripteerde gzip-payloads wat die sleutel gebruik wat in `theme/ht_searcher.js` gedefinieer is.

## Bou en validering

Algemene plaaslike kontroles:

- `node --check theme/ht_searcher.js`
- `mdbook build`

As `mdbook build` misluk, kontroleer:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Redigeringsnotas

- Verkies `rg` vir soektogte.
- Hou gegenereerde `book/`-output uit commits, tensy dit uitdruklik versoek word. Search-loader-regstellings is 'n uitsondering wanneer die reeds geboude bladsye onmiddellik reggestel moet word.
- As gedeelde theme-gedrag verander word, vergelyk en werk die ooreenstemmende lêer in
`/Users/carlospolop/git/hacktricks` by.
- Moenie onverwante plaaslike veranderinge terugrol nie.
