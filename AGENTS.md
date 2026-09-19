# AGENTS.md

Riglyne vir toekomstige agents wat in hierdie repository werk.

## Repository-konteks

Dit is die HackTricks Cloud mdBook-repository. Die verwante hoofboek is by:

`/Users/carlospolop/git/hacktricks`

Veranderinge aan gedeelde theme/search-gedrag moet dikwels in albei repositories toegepas word.

## Laaikontrak vir soekindekse

Die pasgemaakte search UI is in:

`theme/ht_searcher.js`

Daar kan ook ’n gegenereerde kopie wees by:

`book/theme/ht_searcher.js`

As production die reeds geboude `book/`-directory ontplooi, dateer albei kopieë op of bou die
book weer.

Die bronbeleid vir die search index is belangrik en koste-sensitief:

- Op public hosts, laai elke taalspesifieke en fallback-kandidaat slegs vanaf
`HackTricks-wiki/hacktricks-searchindex`. Moet nooit na dieselfde-origin mdBook-output terugval nie;
om die groot index vanaf `cloud.hacktricks.wiki` in production te bedien, is duur.
- Op localhost, `.local`/`.internal`-hosts, loopback, RFC1918, carrier-grade NAT, link-local of
private IPv6-adresse, laai slegs die dieselfde-origin mdBook-output sodat
local/container-deployments selfstandig bly. Vir ’n nie-Engelse bladsy, probeer eers die
taalgeprefikseerde local path (byvoorbeeld `/es/searchindex.js`) en gebruik die root English index
slegs as fallback.

Vir hierdie repo is die verwagte local fallback:

`/searchindex.js`

Die fallback vir die main book vir hierdie repo is:

`/searchindex-book.js`

Daardie local files is slegs private-network-bronne. Public hosts moet die remote
`searchindex-<lang>.js.gz`- en `searchindex-cloud-<lang>.js.gz`-files in
`HackTricks-wiki/hacktricks-searchindex` eksklusief gebruik.

## Publisering van soekindekse

Die workflows wat encrypted compressed search indexes na
`HackTricks-wiki/hacktricks-searchindex` publiseer, is:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die gegenereerde source file is `book/searchindex.js`. Die gepubliseerde remote artifact-name is:

- `searchindex-cloud-v2-en.json.gz` (voorkeur compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (voorkeur compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Die browser loader verkies die compact v2-artifact en behou die `.js.gz`-artifact as ’n legacy
fallback. Albei is XOR-encrypted gzip-payloads wat die sleutel gebruik wat in
`theme/ht_searcher.js` gedefinieer word.

Die loader moet lazy bly: normale page navigation mag nie die search worker skep of ’n index
aflaai voordat die besoeker search oopmaak of gebruik nie. Remote compressed responses word vir
24 uur per origin in Cache Storage behou sodat daaropvolgende bladsye dit kan hergebruik. Behou die
stale-cache-fallback wanneer die verfrissing van ’n vervalde entry misluk.

## Bou en validering

Algemene local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

As `mdbook build` misluk, kontroleer:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Redigeringsaantekeninge

- Verkies `rg` vir searching.
- Hou gegenereerde `book/`-output uit commits, tensy dit uitdruklik versoek word. Search loader-fixes
is ’n uitsondering wanneer die reeds geboude bladsye onmiddellik reggestel moet word.
- As gedeelde theme-gedrag verander word, vergelyk en dateer die ooreenstemmende file in
`/Users/carlospolop/git/hacktricks` op.
- Moenie onverwante plaaslike veranderinge terugstel nie.
