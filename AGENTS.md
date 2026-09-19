# AGENTS.md

Smernice za buduće agente koji rade u ovom repository-ju.

## Kontekst repository-ja

Ovo je HackTricks Cloud mdBook repository. Povezana glavna knjiga nalazi se na:

`/Users/carlospolop/git/hacktricks`

Promene ponašanja deljenog theme/search sistema često moraju da se primene u oba repository-ja.

## Ugovor za učitavanje search index-a

Prilagođeni search UI nalazi se u:

`theme/ht_searcher.js`

Može postojati i generisana kopija na:

`book/theme/ht_searcher.js`

Ako se u production-u deploy-uje već izgrađeni `book/` direktorijum, ažurirajte obe kopije ili ponovo izgradite
book pre deploy-a.

Redosled učitavanja search index-a je važan i osetljiv na troškove:

1. Učitajte svaki language-specific i fallback search index iz GitHub repository-ja:
`HackTricks-wiki/hacktricks-searchindex`
2. Samo ako svi kandidati hostovani na GitHub-u ne uspeju, pređite na isti-origin mdBook output.

Nemojte postavljati lokalni `/searchindex.js` fallback pre bilo kog GitHub-hostovanog fallback-a, kao što je
`searchindex-cloud-en.js.gz`. Serviranje `searchindex.js` sa `cloud.hacktricks.wiki` u production-u je skupo.

Za ovaj repo očekivani lokalni fallback je:

`/searchindex.js`

Fallback glavne knjige za ovaj repo je:

`/searchindex-book.js`

Ovaj fajl je samo fallback. Primarni izvor moraju ostati udaljeni
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` fajlovi u
`HackTricks-wiki/hacktricks-searchindex`.

## Objavljivanje search index-a

Workflow-i koji objavljuju enkriptovane kompresovane search index-e u `HackTricks-wiki/hacktricks-searchindex` su:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generisani source fajl je `book/searchindex.js`. Imena objavljenih udaljenih artifact-a su:

- `searchindex-cloud-v2-en.json.gz` (preferirani kompaktni index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferirani kompaktni index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader daje prednost v2 compact artifact-u i zadržava `.js.gz` artifact kao legacy
fallback. Oba su XOR-enkriptovani gzip payload-i koji koriste ključ definisan u `theme/ht_searcher.js`.

Loader mora ostati lazy: normalna navigacija između stranica ne sme kreirati search worker niti preuzimati index dok posetilac ne otvori ili ne koristi search. Udaljeni kompresovani odgovori čuvaju se u Cache Storage-u 24 sata po origin-u, tako da naredne stranice mogu da ih ponovo koriste. Sačuvajte stale-cache
fallback kada osvežavanje isteklog unosa ne uspe.

## Build i validacija

Uobičajene lokalne provere:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ako `mdbook build` ne uspe, proverite:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Napomene za uređivanje

- Za pretragu preferirajte `rg`.
- Držite generisani `book/` output van commit-a osim ako to nije izričito zatraženo. Ispravke search loader-a
su izuzetak kada već izgrađene stranice moraju odmah da budu ispravljene.
- Ako menjate ponašanje deljenog theme-a, uporedite i ažurirajte odgovarajući fajl u
`/Users/carlospolop/git/hacktricks`.
- Nemojte vraćati nepovezane lokalne promene.
