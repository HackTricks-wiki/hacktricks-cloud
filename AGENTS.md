# AGENTS.md

Smernice za buduće agente koji rade u ovom repozitorijumu.

## Kontekst repozitorijuma

Ovo je HackTricks Cloud mdBook repozitorijum. Povezana glavna knjiga se nalazi na:

`/Users/carlospolop/git/hacktricks`

Promene u deljenom theme/search ponašanju često moraju da se primene u oba repozitorijuma.

## Search Index Loading Contract

Prilagođeni search UI se nalazi u:

`theme/ht_searcher.js`

Može postojati i generisana kopija na:

`book/theme/ht_searcher.js`

Ako se u produkciji deploy-uje već izgrađeni `book/` direktorijum, ažuriraj obe kopije ili ponovo izgradi knjigu pre deploy-a.

Redosled učitavanja search index-a je važan i osetljiv na troškove:

1. Učitaj svaki jezički specifičan i fallback search index iz GitHub repozitorijuma:
`HackTricks-wiki/hacktricks-searchindex`
2. Samo ako svi GitHub-hosted kandidati fail-uju, pređi na same-origin mdBook output.

Ne stavljaj lokalni `/searchindex.js` fallback pre bilo kog GitHub-hosted fallback-a kao što je
`searchindex-cloud-en.js.gz`. Serviranje `searchindex.js` sa `cloud.hacktricks.wiki` u produkciji je skupo.

Za ovaj repozitorijum, očekivani lokalni fallback je:

`/searchindex.js`

Fallback glavne knjige za ovaj repozitorijum je:

`/searchindex-book.js`

Ta datoteka je samo fallback. Primarni izvor mora ostati remote
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` fajlovi u
`HackTricks-wiki/hacktricks-searchindex`.

## Search Index Publishing

Workflows koji objavljuju encrypted compressed search indexes u
`HackTricks-wiki/hacktricks-searchindex` su:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generisana source datoteka je `book/searchindex.js`. Nazivi objavljenih remote artifact-a su:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader očekuje da su remote `.js.gz` fajlovi XOR-encrypted gzip payload-i koristeći
ključ definisan u `theme/ht_searcher.js`.

## Build And Validation

Uobičajene lokalne provere:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ako `mdbook build` fail-uje, proveri:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Preferiraj `rg` za pretragu.
- Drži generisani `book/` output van commit-ova osim ako nije izričito traženo. Ispravke search loader-a su izuzetak kada već izgrađene stranice moraju odmah da se poprave.
- Ako menjaš deljeno theme ponašanje, uporedi i ažuriraj odgovarajuću datoteku u
`/Users/carlospolop/git/hacktricks`.
- Ne vraćaj nepovezane lokalne izmene.
