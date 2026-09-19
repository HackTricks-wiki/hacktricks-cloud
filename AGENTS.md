# AGENTS.md

Mwongozo kwa agents wa baadaye wanaofanya kazi katika repository hii.

## Muktadha wa Repository

Hii ni repository ya HackTricks Cloud mdBook. Kitabu kikuu kinachohusiana kinapatikana kwenye:

`/Users/carlospolop/git/hacktricks`

Mabadiliko kwenye tabia ya shared theme/search mara nyingi yanahitaji kutekelezwa katika repositories zote mbili.

## Mkataba wa Kupakia Search Index

UI maalum ya search iko kwenye:

`theme/ht_searcher.js`

Huenda pia kukawa na nakala iliyotengenezwa kwenye:

`book/theme/ht_searcher.js`

Ikiwa production inadeploy directory ya `book/` iliyokwisha tengenezwa, sasisha nakala zote mbili au rebuild kitabu kabla ya deployment.

Mpangilio wa kupakia search index ni muhimu na una gharama:

1. Pakia kila search index ya lugha maalum na fallback kutoka GitHub repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Ni pale tu candidates zote zinazohifadhiwa na GitHub zinaposhindwa ndipo utumie fallback ya mdBook output kutoka same-origin.

Usiweke fallback ya local `/searchindex.js` kabla ya fallback yoyote inayohifadhiwa na GitHub kama `searchindex-cloud-en.js.gz`. Kutumikia `searchindex.js` kutoka `cloud.hacktricks.wiki` kwenye production kuna gharama kubwa.

Kwa repository hii, local fallback inayotarajiwa ni:

`/searchindex.js`

Main-book fallback ya repository hii ni:

`/searchindex-book.js`

Faili hiyo ni fallback pekee. Chanzo kikuu lazima kibaki kuwa faili za mbali za
`searchindex-<lang>.js.gz` na `searchindex-cloud-<lang>.js.gz` kwenye
`HackTricks-wiki/hacktricks-searchindex`.

## Kuchapisha Search Index

Workflows zinazochapisha search index zilizobanwa na kusimbwa kwa encryption kwenye `HackTricks-wiki/hacktricks-searchindex` ni:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Faili ya source inayotengenezwa ni `book/searchindex.js`. Majina ya remote artifacts zinazochapishwa ni:

- `searchindex-cloud-v2-en.json.gz` (compact index inayopendelewa)
- `searchindex-cloud-v2-<lang>.json.gz` (compact index inayopendelewa)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader hupendelea compact v2 artifact na huhifadhi artifact ya `.js.gz` kama legacy fallback. Zote mbili ni XOR-encrypted gzip payloads zinazotumia key iliyofafanuliwa kwenye `theme/ht_searcher.js`.

Loader lazima ibaki lazy: page navigation ya kawaida haipaswi kuunda search worker au kupakua index hadi visitor afungue au atumie search. Remote compressed responses huhifadhiwa kwenye Cache Storage kwa saa 24 kwa kila origin ili pages zinazofuata ziweze kuzitumia tena. Hifadhi stale-cache fallback wakati refresh ya entry iliyokwisha muda inashindwa.

## Build Na Validation

Ukaguzi wa kawaida wa local:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ikiwa `mdbook build` itashindwa, angalia:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Maelezo ya Kuhariri

- Pendelea `rg` kwa kutafuta.
- Weka output ya `book/` iliyotengenezwa nje ya commits isipokuwa ikiwa imeombwa wazi. Marekebisho ya search loader ni exception wakati pages zilizokwisha tengenezwa lazima zisahihishwe mara moja.
- Ukibadilisha tabia ya shared theme, linganisha na usasishe faili inayolingana katika
`/Users/carlospolop/git/hacktricks`.
- Usirevert mabadiliko ya local yasiyohusiana.
