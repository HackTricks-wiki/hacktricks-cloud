# AGENTS.md

Mwongozo kwa agents wa baadaye wanaofanya kazi katika repository hii.

## Muktadha wa Repository

Hii ni repository ya HackTricks Cloud mdBook. Kitabu kikuu kinachohusiana kinapatikana katika:

`/Users/carlospolop/git/hacktricks`

Mabadiliko ya tabia ya theme/search mara nyingi yanahitaji kutekelezwa katika repositories zote mbili.

## Mkataba wa Kupakia Search Index

Custom search UI iko katika:

`theme/ht_searcher.js`

Huenda pia kukawa na nakala iliyotengenezwa katika:

`book/theme/ht_searcher.js`

Ikiwa production inadeploy directory ya `book/` iliyokwisha kujengwa, sasisha nakala zote mbili au build upya kitabu kabla ya deployment.

Policy ya chanzo cha search index ni muhimu na inazingatia gharama:

- Kwenye public hosts, pakia kila language-specific na fallback candidate kutoka
`HackTricks-wiki/hacktricks-searchindex` pekee. Usitumie kamwe mdBook output ya same-origin kama fallback; ku-serve index kubwa kutoka `cloud.hacktricks.wiki` katika production ni ghali.
- Kwenye localhost, hosts za `.local`/`.internal`, loopback, RFC1918, carrier-grade NAT, link-local, au private IPv6 addresses, pakia mdBook output ya same-origin pekee ili local/container deployments zibaki self-contained.

Kwa repository hii, local fallback inayotarajiwa ni:

`/searchindex.js`

Main-book fallback ya repository hii ni:

`/searchindex-book.js`

Local files hizo ni private-network sources pekee. Public hosts lazima zitumie remote
`searchindex-<lang>.js.gz` na `searchindex-cloud-<lang>.js.gz` files zilizo katika
`HackTricks-wiki/hacktricks-searchindex` pekee.

## Kuchapisha Search Index

Workflows zinazochapisha search indexes zilizosimbwa na kubanwa kwenda
`HackTricks-wiki/hacktricks-searchindex` ni:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file ni `book/searchindex.js`. Majina ya remote artifacts zilizochapishwa ni:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader hupendelea compact v2 artifact na huhifadhi `.js.gz` artifact kama legacy
fallback. Zote mbili ni XOR-encrypted gzip payloads zinazotumia key iliyofafanuliwa katika `theme/ht_searcher.js`.

Loader lazima ibaki lazy: page navigation ya kawaida haipaswi kuunda search worker au kupakua index hadi visitor afungue au atumie search. Remote compressed responses huhifadhiwa katika Cache Storage kwa saa 24 kwa kila origin, ili pages zinazofuata ziweze kuzitumia tena. Hifadhi stale-cache fallback wakati refresh ya entry iliyo-expire inashindikana.

## Build Na Validation

Common local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ikiwa `mdbook build` itashindikana, angalia:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Maelezo ya Kuhariri

- Pendelea `rg` kwa ajili ya kutafuta.
- Weka generated `book/` output nje ya commits isipokuwa imeombwa wazi. Search loader fixes ni exception ikiwa pages zilizokwisha kujengwa lazima zisahihishwe mara moja.
- Ukibadilisha tabia ya shared theme, linganisha na usasishe file inayolingana katika
`/Users/carlospolop/git/hacktricks`.
- Usirevert mabadiliko ya local yasiyohusiana.
