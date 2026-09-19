# AGENTS.md

Smernice za buduće agente koji rade u ovom repozitorijumu.

## Kontekst repozitorijuma

Ovo je HackTricks Cloud mdBook repozitorijum. Povezana glavna knjiga nalazi se na:

`/Users/carlospolop/git/hacktricks`

Promene zajedničkog ponašanja teme/pretrage često treba primeniti u oba repozitorijuma.

## Ugovor o učitavanju indeksa pretrage

Prilagođeni interfejs pretrage nalazi se u:

`theme/ht_searcher.js`

Možda postoji i generisana kopija na:

`book/theme/ht_searcher.js`

Ako se u produkciju postavlja već izgrađeni direktorijum `book/`, ažurirajte obe kopije ili ponovo izgradite knjigu.

Redosled učitavanja indeksa pretrage je važan i osetljiv na troškove:

1. Učitajte svaki jezički specifičan indeks pretrage i rezervni indeks iz GitHub repozitorijuma:
`HackTricks-wiki/hacktricks-searchindex`
2. Samo ako svi kandidati hostovani na GitHubu ne uspeju, pređite na isti-origin mdBook izlaz.

Ne postavljajte lokalni `/searchindex.js` fallback ispred bilo kog GitHub fallback-a, kao što je
`searchindex-cloud-en.js.gz`. Posluživanje `searchindex.js` sa `cloud.hacktricks.wiki` u produkciji je skupo.

Za ovaj repozitorijum očekivani lokalni fallback je:

`/searchindex.js`

Fallback glavne knjige za ovaj repozitorijum je:

`/searchindex-book.js`

Ovaj fajl je samo fallback. Primarni izvor moraju ostati udaljeni fajlovi
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` u
`HackTricks-wiki/hacktricks-searchindex`.

## Objavljivanje indeksa pretrage

Workflow-i koji objavljuju šifrovane kompresovane indekse pretrage u `HackTricks-wiki/hacktricks-searchindex` su:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generisani izvorni fajl je `book/searchindex.js`. Nazivi objavljenih udaljenih artefakata su:

- `searchindex-cloud-v2-en.json.gz` (poželjni kompaktni indeks)
- `searchindex-cloud-v2-<lang>.json.gz` (poželjni kompaktni indeks)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Učitavač u pregledaču daje prednost v2 kompaktom artefaktu i zadržava `.js.gz` artefakt kao legacy fallback. Oba su XOR-šifrovani gzip sadržaji koji koriste ključ definisan u `theme/ht_searcher.js`.

## Izgradnja i validacija

Uobičajene lokalne provere:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ako `mdbook build` ne uspe, proverite:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Napomene o izmenama

- Prednost dajte alatu `rg` za pretragu.
- Držite generisani `book/` izlaz van commit-a, osim ako to nije izričito zatraženo. Ispravke učitavača pretrage su izuzetak kada već izgrađene stranice moraju odmah biti ispravljene.
- Ako menjate ponašanje zajedničke teme, uporedite i ažurirajte odgovarajući fajl u
`/Users/carlospolop/git/hacktricks`.
- Ne vraćajte nepovezane lokalne izmene.
