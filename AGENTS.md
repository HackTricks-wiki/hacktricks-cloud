# AGENTS.md

Smernice za buduće agente koji rade u ovom repozitorijumu.

## Kontekst repozitorijuma

Ovo je HackTricks Cloud mdBook repozitorijum. Povezana glavna knjiga nalazi se na:

`/Users/carlospolop/git/hacktricks`

Promene ponašanja deljenog theme/search sistema često treba primeniti u oba repozitorijuma.

## Ugovor za učitavanje indeksa pretrage

Prilagođeni search UI nalazi se u:

`theme/ht_searcher.js`

Može postojati i generisana kopija na:

`book/theme/ht_searcher.js`

Ako production koristi već izgrađeni `book/` direktorijum, ažurirajte obe kopije ili ponovo izgradite
knjigu pre deploymenta.

Pravila za izvor search indexa su važna i osetljiva u pogledu troškova:

- Na javnim hostovima učitavajte svakog kandidata specifičnog za jezik i fallback kandidata isključivo iz
`HackTricks-wiki/hacktricks-searchindex`. Nikada nemojte koristiti fallback ka mdBook outputu sa istog origin-a;
serviranje velikog indexa sa `cloud.hacktricks.wiki` u productionu je skupo.
- Na localhost, `.local`/`.internal` hostovima, loopback adresama, RFC1918 adresama, carrier-grade NAT adresama, link-local adresama ili
privatnim IPv6 adresama, učitavajte samo mdBook output sa istog origin-a kako bi lokalni/container deploymenti
ostali samostalni.

Za ovaj repozitorijum očekivani lokalni fallback je:

`/searchindex.js`

Fallback za main-book je:

`/searchindex-book.js`

Ovi lokalni fajlovi su izvori samo za privatne mreže. Javni hostovi moraju isključivo koristiti udaljene
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` fajlove iz
`HackTricks-wiki/hacktricks-searchindex`.

## Objavljivanje search indexa

Workflow-i koji objavljuju enkriptovane kompresovane search indexe u `HackTricks-wiki/hacktricks-searchindex` su:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generisani izvorni fajl je `book/searchindex.js`. Nazivi objavljenih udaljenih artifacta su:

- `searchindex-cloud-v2-en.json.gz` (preferirani kompaktni index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferirani kompaktni index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader daje prednost v2 compact artifactu i zadržava `.js.gz` artifact kao legacy
fallback. Oba su XOR-enkriptovani gzip payloadi koji koriste ključ definisan u `theme/ht_searcher.js`.

Loader mora ostati lazy: normalna navigacija stranica ne sme kreirati search worker niti preuzimati index dok posetilac ne otvori ili ne koristi search. Udaljeni kompresovani odgovori čuvaju se u Cache Storage-u tokom 24 sata po originu, kako bi naredne stranice mogle da ih ponovo koriste. Sačuvajte fallback ka zastarelom cache-u kada osvežavanje isteklog unosa ne uspe.

## Build i validacija

Uobičajene lokalne provere:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Ako `mdbook build` ne uspe, proverite:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Napomene za uređivanje

- Za pretragu preferirajte `rg`.
- Držite generisani `book/` output izvan commit-a, osim ako to nije izričito zatraženo. Izmene search loadera predstavljaju
izuzetak kada već izgrađene stranice moraju odmah biti ispravljene.
- Ako menjate ponašanje deljenog theme-a, uporedite i ažurirajte odgovarajući fajl u
`/Users/carlospolop/git/hacktricks`.
- Ne vraćajte nepovezane lokalne izmene.
