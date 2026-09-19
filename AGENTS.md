# AGENTS.md

Linee guida per i futuri agent che lavorano in questo repository.

## Contesto del repository

Questo è il repository mdBook di HackTricks Cloud. Il libro principale correlato si trova in:

`/Users/carlospolop/git/hacktricks`

Le modifiche al comportamento condiviso di theme/search spesso devono essere applicate in entrambi i repository.

## Contratto di caricamento dell'indice di ricerca

L'interfaccia custom di search si trova in:

`theme/ht_searcher.js`

Potrebbe inoltre esserci una copia generata in:

`book/theme/ht_searcher.js`

Se la produzione effettua il deploy della directory `book/` già compilata, aggiorna entrambe le copie oppure ricompila il
book prima del deployment.

La policy relativa alla sorgente dell'indice di search è importante e sensibile ai costi:

- Sugli host pubblici, carica ogni candidato specifico per la lingua e di fallback esclusivamente da
`HackTricks-wiki/hacktricks-searchindex`. Non usare mai come fallback l'output mdBook della stessa origine;
servire l'indice di grandi dimensioni da `cloud.hacktricks.wiki` in produzione è costoso.
- Su localhost, host `.local`/`.internal`, loopback, RFC1918, carrier-grade NAT, link-local o indirizzi IPv6
privati, carica solo l'output mdBook della stessa origine, in modo che i deployment locali/container
rimangano autosufficienti. Per una pagina non inglese, prova prima il percorso locale con prefisso della lingua
(ad esempio `/es/searchindex.js`) e usa l'indice inglese root solo come fallback.

Per questo repo, il fallback locale previsto è:

`/searchindex.js`

Il fallback del libro principale per questo repo è:

`/searchindex-book.js`

Questi file locali sono sorgenti esclusivamente per reti private. Gli host pubblici devono usare solo i file remoti
`searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex`.

## Pubblicazione dell'indice di search

I workflow che pubblicano gli indici di search compressi e cifrati su
`HackTricks-wiki/hacktricks-searchindex` sono:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Il file sorgente generato è `book/searchindex.js`. I nomi degli artifact remoti pubblicati sono:

- `searchindex-cloud-v2-en.json.gz` (indice compatto preferito)
- `searchindex-cloud-v2-<lang>.json.gz` (indice compatto preferito)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Il browser loader preferisce l'artifact compatto v2 e mantiene l'artifact `.js.gz` come fallback legacy. Entrambi sono
payload gzip cifrati con XOR usando la chiave definita in `theme/ht_searcher.js`.

Il loader deve rimanere lazy: la normale navigazione tra le pagine non deve creare il search worker o scaricare un
indice finché il visitatore non apre o utilizza la search. Le risposte remote compresse vengono salvate in Cache
Storage per 24 ore per origin, così le pagine successive possono riutilizzarle. Mantieni il fallback alla cache
stale quando il refresh di una voce scaduta fallisce.

## Build e validazione

Controlli locali comuni:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` fallisce, controlla:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Note sulle modifiche

- Preferisci `rg` per le ricerche.
- Mantieni l'output `book/` generato fuori dai commit, salvo esplicita richiesta. Le correzioni al search loader
sono un'eccezione quando le pagine già compilate devono essere corrette immediatamente.
- Se modifichi il comportamento del theme condiviso, confronta e aggiorna il file corrispondente in
`/Users/carlospolop/git/hacktricks`.
- Non annullare modifiche locali non correlate.
