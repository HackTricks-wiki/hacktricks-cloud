# AGENTS.md

Mwongozo kwa mawakala wa baadaye wanaofanya kazi katika repo hii.

## Muktadha wa Repository

Hii ni repository ya HackTricks Cloud mdBook. Kitabu kikuu kinachohusiana kiko katika:

`/Users/carlospolop/git/hacktricks`

Mabadiliko kwenye shared theme/search behavior mara nyingi yanahitaji kutumika katika repo zote mbili.

## Search Index Loading Contract

Custom search UI iko katika:

`theme/ht_searcher.js`

Huenda pia kuna copy iliyozalishwa katika:

`book/theme/ht_searcher.js`

Ikiwa production inasambaza directory iliyokwisha-jengwa `book/`, sasisha nakala zote mbili au jenga upya
kitabu kabla ya deployment.

Mpangilio wa kupakia search index ni muhimu na unagharimu rasilimali:

1. Pakia kila search index ya lugha mahususi na fallback search index kutoka GitHub repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Ni ikiwa tu wagombea wote wanaohostiwa na GitHub watafail, tumia fallback ya same-origin mdBook output.

Usiweke local `/searchindex.js` fallback kabla ya fallback yoyote inayohostiwa na GitHub kama
`searchindex-cloud-en.js.gz`. Kuhudumia `searchindex.js` kutoka `cloud.hacktricks.wiki` katika production ni gharama kubwa.

Kwa repo hii, expected local fallback ni:

`/searchindex.js`

Main-book fallback kwa repo hii ni:

`/searchindex-book.js`

Faili hiyo ni fallback tu. Chanzo cha msingi lazima kiendelee kuwa remote
`searchindex-<lang>.js.gz` na `searchindex-cloud-<lang>.js.gz` files katika
`HackTricks-wiki/hacktricks-searchindex`.

## Search Index Publishing

Workflows zinazochapisha encrypted compressed search indexes kwenda
`HackTricks-wiki/hacktricks-searchindex` ni:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file ni `book/searchindex.js`. Majina ya published remote artifact ni:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader inatarajia remote `.js.gz` files ziwe XOR-encrypted gzip payloads zinazotumia
key iliyofafanuliwa katika `theme/ht_searcher.js`.

## Build And Validation

Ukaguzi wa kawaida wa local:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ikiwa `mdbook build` itafeli, angalia:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Pendelea `rg` kwa kutafuta.
- Weka generated `book/` output nje ya commits isipokuwa ikiombwa waziwazi. Search loader fixes ni
exception wakati pages zilizokwisha-jengwa zinahitaji kusahihishwa mara moja.
- Ikiwa unabadilisha shared theme behavior, linganisha na urekebishe faili linalolingana katika
`/Users/carlospolop/git/hacktricks`.
- Usirudishe mabadiliko ya ndani yasiyohusiana.
