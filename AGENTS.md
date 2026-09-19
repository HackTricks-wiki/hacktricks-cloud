# AGENTS.md

Mwongozo kwa agents wa baadaye wanaofanya kazi katika repository hii.

## Muktadha wa Repository

Hii ni repository ya HackTricks Cloud mdBook. Kitabu kikuu kinachohusiana kinapatikana katika:

`/Users/carlospolop/git/hacktricks`

Mabadiliko ya tabia ya theme/search inayoshirikiwa mara nyingi yanahitaji kutekelezwa katika repositories zote mbili.

## Mkataba wa Kupakia Search Index

Search UI maalum inapatikana katika:

`theme/ht_searcher.js`

Huenda pia kukawa na nakala iliyotengenezwa katika:

`book/theme/ht_searcher.js`

Ikiwa production inadeploy directory ya `book/` iliyokwisha kujengwa, sasisha nakala zote mbili au rebuild kitabu kabla ya deployment.

Policy ya chanzo cha search index ni muhimu na inazingatia gharama:

- Kwenye public hosts, pakia kila language-specific na fallback candidate kutoka `HackTricks-wiki/hacktricks-searchindex` pekee. Usitumie kamwe mdBook output ya same-origin kama fallback; kutumikia index kubwa kutoka `cloud.hacktricks.wiki` kwenye production ni ghali.
- Kwenye localhost, hosts za `.local`/`.internal`, loopback, RFC1918, carrier-grade NAT, link-local, au private IPv6 addresses, pakia mdBook output ya same-origin pekee ili local/container deployments zibaki self-contained. Kwa ukurasa usio wa Kiingereza, jaribu kwanza local path yenye language prefix (kwa mfano `/es/searchindex.js`) na utumie root English index kama fallback pekee.

Kwa repository hii, local fallback inayotarajiwa ni:

`/searchindex.js`

Main-book fallback ya repository hii ni:

`/searchindex-book.js`

Local files hizo ni private-network sources pekee. Public hosts lazima zitumie remote
`searchindex-<lang>.js.gz` na `searchindex-cloud-<lang>.js.gz` files katika `HackTricks-wiki/hacktricks-searchindex` pekee.

## Kuchapisha Search Index

Workflows zinazopublish encrypted compressed search indexes kwenye
`HackTricks-wiki/hacktricks-searchindex` ni:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file ni `book/searchindex.js`. Majina ya published remote artifacts ni:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader hupendelea compact v2 artifact na huhifadhi `.js.gz` artifact kama legacy fallback. Zote mbili ni XOR-encrypted gzip payloads zinazotumia key iliyofafanuliwa katika `theme/ht_searcher.js`.

Loader lazima ibaki lazy: page navigation ya kawaida haipaswi kuunda search worker au kupakua index hadi visitor afungue au atumie search. Remote compressed responses huhifadhiwa katika Cache Storage kwa saa 24 kwa kila origin ili pages zinazofuata ziweze kuzitumia tena. Hifadhi stale-cache fallback wakati refreshing expired entry kunaposhindikana.

## Build Na Validation

Checks za kawaida za local:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ikiwa `mdbook build` itashindikana, angalia:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Maelezo ya Kuhariri

- Pendelea `rg` kwa kutafuta.
- Weka generated `book/` output nje ya commits isipokuwa ikiwa imeombwa wazi. Search loader fixes ni exception wakati pages zilizokwisha kujengwa lazima zirekebishwe mara moja.
- Ukibadilisha shared theme behavior, linganisha na usasishe file inayolingana katika
`/Users/carlospolop/git/hacktricks`.
- Usirevert local changes zisizohusiana.
