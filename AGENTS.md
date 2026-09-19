# AGENTS.md

Smernice za buduće agente koji rade u ovom repozitorijumu.

## Kontekst repozitorijuma

Ovo je HackTricks Cloud mdBook repozitorijum. Povezana glavna knjiga nalazi se na:

`/Users/carlospolop/git/hacktricks`

Promene zajedničkog ponašanja teme/pretrage često je potrebno primeniti u oba repozitorijuma.

## Ugovor za učitavanje indeksa pretrage

Prilagođeni UI za pretragu nalazi se u:

`theme/ht_searcher.js`

Može postojati i generisana kopija na:

`book/theme/ht_searcher.js`

Ako production deploy-uje već izgrađeni direktorijum `book/`, ažurirajte obe kopije ili ponovo izgradite
book pre deployment-a.

Politika izvora indeksa pretrage je važna i osetljiva je na troškove:

- Na javnim hostovima učitajte svakog kandidata specifičnog za jezik i fallback kandidata isključivo iz
`HackTricks-wiki/hacktricks-searchindex`. Nikada nemojte koristiti isti-origin mdBook output kao fallback;
serviranje velikog indeksa sa `cloud.hacktricks.wiki` u production-u je skupo.
- Na localhost, `.local`/`.internal` hostovima, loopback adresama, RFC1918 adresama, carrier-grade NAT adresama, link-local adresama, IPv6 adresama i privatnim IPv6 adresama, učitajte samo isti-origin mdBook output kako bi lokalni/container deployment-i ostali samostalni. Za stranicu koja nije na engleskom, prvo pokušajte lokalnu putanju sa prefiksom jezika (na primer `/es/searchindex.js`), a root English indeks koristite samo kao fallback.

Očekivani lokalni fallback za ovaj repo je:

`/searchindex.js`

Fallback glavne knjige za ovaj repo je:

`/searchindex-book.js`

Ovi lokalni fajlovi su izvori samo za privatne mreže. Javni hostovi moraju isključivo koristiti udaljene
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` fajlove iz
`HackTricks-wiki/hacktricks-searchindex`.

## Objavljivanje indeksa pretrage

Workflow-i koji objavljuju šifrovane kompresovane indekse pretrage u
`HackTricks-wiki/hacktricks-searchindex` su:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generisani izvorni fajl je `book/searchindex.js`. Objavljena imena udaljenih artefakata su:

- `searchindex-cloud-v2-en.json.gz` (preferirani kompaktni indeks)
- `searchindex-cloud-v2-<lang>.json.gz` (preferirani kompaktni indeks)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader daje prednost v2 kompaktном artefaktu i zadržava `.js.gz` artefakt kao legacy
fallback. Oba su XOR-encrypted gzip payload-i koji koriste ključ definisan u `theme/ht_searcher.js`.

Loader mora ostati lazy: uobičajena navigacija stranicama ne sme kreirati search worker niti preuzimati indeks
dok posetilac ne otvori ili ne upotrebi pretragu. Udaljeni kompresovani odgovori čuvaju se u Cache
Storage-u 24 časa po origin-u, kako bi naredne stranice mogle da ih ponovo koriste. Sačuvajte stale-cache
fallback prilikom osvežavanja isteklog unosa ako osvežavanje ne uspe.

## Build i validacija

Uobičajene lokalne provere:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ako `mdbook build` ne uspe, proverite:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Napomene za uređivanje

- Za pretragu preferirajte `rg`.
- Držite generisani `book/` output izvan commit-ova, osim ako to nije izričito zatraženo. Ispravke search loader-a su
izuzetak kada već izgrađene stranice moraju odmah da budu ispravljene.
- Ako menjate ponašanje zajedničke teme, uporedite i ažurirajte odgovarajući fajl u
`/Users/carlospolop/git/hacktricks`.
- Nemojte vraćati nepovezane lokalne promene.
