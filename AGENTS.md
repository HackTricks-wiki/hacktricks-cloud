# AGENTS.md

Indicazioni per i futuri agent che lavorano in questo repository.

## Contesto del repository

Questo è il repository mdBook di HackTricks Cloud. Il libro principale correlato si trova in:

`/Users/carlospolop/git/hacktricks`

Le modifiche al comportamento condiviso di theme/search spesso devono essere applicate in entrambi i repository.

## Contratto di caricamento del Search Index

La UI di search personalizzata si trova in:

`theme/ht_searcher.js`

Potrebbe esistere anche una copia generata in:

`book/theme/ht_searcher.js`

Se la produzione esegue il deploy della directory `book/` già compilata, aggiorna entrambe le copie oppure ricompila il libro.

L'ordine di caricamento del search index è importante e sensibile ai costi:

1. Carica ogni search index specifico per la lingua e di fallback dal repository GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Solo se tutti i candidati ospitati su GitHub falliscono, esegui il fallback sull'output mdBook della stessa origine.

Non posizionare il fallback locale `/searchindex.js` prima di qualsiasi fallback ospitato su GitHub, come
`searchindex-cloud-en.js.gz`. Servire `searchindex.js` da `cloud.hacktricks.wiki` in produzione è costoso.

Per questo repository, il fallback locale previsto è:

`/searchindex.js`

Il fallback del main-book per questo repository è:

`/searchindex-book.js`

Questo file è solo un fallback. La sorgente primaria deve rimanere costituita dai file remoti
`searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex`.

## Pubblicazione del Search Index

I workflow che pubblicano i search index compressi e crittografati in
`HackTricks-wiki/hacktricks-searchindex` sono:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Il file sorgente generato è `book/searchindex.js`. I nomi degli artifact remoti pubblicati sono:

- `searchindex-cloud-v2-en.json.gz` (compact index preferito)
- `searchindex-cloud-v2-<lang>.json.gz` (compact index preferito)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Il browser loader preferisce l'artifact v2 compatto e mantiene l'artifact `.js.gz` come fallback legacy. Entrambi sono payload gzip crittografati con XOR utilizzando la chiave definita in `theme/ht_searcher.js`.

Il loader deve rimanere lazy: la normale navigazione tra le pagine non deve creare il search worker né scaricare un index finché il visitatore non apre o utilizza la search. Le risposte remote compresse vengono mantenute nella Cache Storage per 24 ore per origin, così le pagine successive possono riutilizzarle. Mantieni il fallback della cache obsoleta quando l'aggiornamento di una voce scaduta fallisce.

## Build e validazione

Controlli locali comuni:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` fallisce, controlla:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Note sulla modifica

- Preferisci `rg` per le ricerche.
- Mantieni l'output `book/` generato fuori dai commit, salvo richiesta esplicita. Le correzioni al search loader fanno eccezione quando le pagine già compilate devono essere corrette immediatamente.
- Se modifichi il comportamento condiviso del theme, confronta e aggiorna il file corrispondente in
`/Users/carlospolop/git/hacktricks`.
- Non annullare le modifiche locali non correlate.
