# AGENTS.md

Linee guida per i futuri agenti che lavorano in questo repository.

## Contesto del Repository

Questo è il repository mdBook di HackTricks Cloud. Il libro principale correlato si trova in:

`/Users/carlospolop/git/hacktricks`

Le modifiche al comportamento condiviso di theme/search spesso devono essere applicate in entrambi i repository.

## Contratto di Caricamento dell'Indice di Ricerca

La custom search UI si trova in:

`theme/ht_searcher.js`

Potrebbe esserci anche una copia generata in:

`book/theme/ht_searcher.js`

Se la produzione distribuisce la directory `book/` già compilata, aggiorna entrambe le copie oppure ricostruisci il libro prima del deployment.

L'ordine di caricamento dell'indice di ricerca è importante e sensibile ai costi:

1. Carica ogni indice di ricerca specifico per lingua e fallback dal repository GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Solo se tutti i candidate ospitati su GitHub falliscono, fai fallback allo stesso origin dell'output mdBook.

Non mettere il fallback locale `/searchindex.js` prima di qualsiasi fallback ospitato su GitHub come
`searchindex-cloud-en.js.gz`. Servire `searchindex.js` da `cloud.hacktricks.wiki` in produzione è costoso.

Per questo repository, il fallback locale previsto è:

`/searchindex.js`

Il main-book fallback per questo repository è:

`/searchindex-book.js`

Quel file è solo un fallback. La primary source deve rimanere i file remoti
`searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex`.

## Pubblicazione dell'Indice di Ricerca

I workflow che pubblicano gli indici di ricerca compressi e cifrati in
`HackTricks-wiki/hacktricks-searchindex` sono:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Il file sorgente generato è `book/searchindex.js`. I nomi degli artifact remoti pubblicati sono:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Il browser loader si aspetta i file remoti `.js.gz` come payload gzip cifrati con XOR usando la
key definita in `theme/ht_searcher.js`.

## Build E Validazione

Controlli locali comuni:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` fallisce, controlla:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Note di Editing

- Preferisci `rg` per cercare.
- Mantieni l'output generato `book/` fuori dai commit, a meno che non sia richiesto esplicitamente. Le correzioni del search loader sono
un'eccezione quando le pagine già compilate devono essere corrette immediatamente.
- Se modifichi il comportamento condiviso di theme, confronta e aggiorna il file corrispondente in
`/Users/carlospolop/git/hacktricks`.
- Non revertire modifiche locali non correlate.
