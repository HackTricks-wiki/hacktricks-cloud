# AGENTS.md

Riglyne vir toekomstige agente wat in hierdie repository werk.

## Repository Context

Hierdie is die HackTricks Cloud mdBook repository. Die verwante hoofboek is by:

`/Users/carlospolop/git/hacktricks`

Veranderings aan gedeelde tema/soek-gedrag moet dikwels in albei repositories toegepas word.

## Search Index Loading Contract

Die pasgemaakte soek-UI is in:

`theme/ht_searcher.js`

Daar mag ook ’n gegenereerde kopie wees by:

`book/theme/ht_searcher.js`

As production die reeds-geboude `book/` gids ontplooi, werk albei kopieë by of bou die
boek weer voor ontplooiing.

Die soekindeks-laaivolgorde is belangrik en koste-gevoelig:

1. Laai elke taal-spesifieke en fallback soekindeks vanaf die GitHub repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Slegs as alle GitHub-gehoste kandidate faal, val terug na die selfde-oorsprong mdBook-uitset.

Moenie die plaaslike `/searchindex.js` fallback voor enige GitHub-gehoste fallback soos
`searchindex-cloud-en.js.gz` plaas nie. Om `searchindex.js` vanaf `cloud.hacktricks.wiki` in production te bedien is duur.

Vir hierdie repo is die verwagte plaaslike fallback:

`/searchindex.js`

Die hoof-boek fallback vir hierdie repo is:

`/searchindex-book.js`

Daardie lêer is slegs ’n fallback. Die primêre bron moet die remote
`searchindex-<lang>.js.gz` en `searchindex-cloud-<lang>.js.gz` lêers in
`HackTricks-wiki/hacktricks-searchindex` bly.

## Search Index Publishing

Die workflows wat geënkripteerde gekompresseerde soekindekse na
`HackTricks-wiki/hacktricks-searchindex` publiseer, is:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die gegenereerde bronlêer is `book/searchindex.js`. Die gepubliseerde remote artifact name is:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Die browser loader verwag die remote `.js.gz` lêers om XOR-geënkripteerde gzip-payloads te wees met die
sleutel gedefinieer in `theme/ht_searcher.js`.

## Build And Validation

Algemene plaaslike kontroles:

- `node --check theme/ht_searcher.js`
- `mdbook build`

As `mdbook build` misluk, kyk na:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Verkies `rg` vir soek.
- Hou gegenereerde `book/` uitsette uit commits tensy uitdruklik versoek. Regstellings aan die soeklaaier is
’n uitsondering wanneer die reeds-geboude bladsye onmiddellik reggestel moet word.
- As gedeelde tema-gedrag verander, vergelyk en werk die ooreenstemmende lêer in
`/Users/carlospolop/git/hacktricks`.
- Moenie onverwante plaaslike veranderings terugdraai nie.
