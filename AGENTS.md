# AGENTS.md

Indicazioni per i futuri agent che lavorano in questo repository.

## Contesto del repository

Questo è il repository mdBook di HackTricks Cloud. Il libro principale correlato si trova in:

`/Users/carlospolop/git/hacktricks`

Le modifiche al comportamento condiviso del tema e della ricerca spesso devono essere applicate in entrambi i repository.

## Contratto di caricamento dell'indice di ricerca

L'interfaccia di ricerca personalizzata si trova in:

`theme/ht_searcher.js`

Potrebbe esserci anche una copia generata in:

`book/theme/ht_searcher.js`

Se la produzione esegue il deploy della directory `book/` già compilata, aggiorna entrambe le copie oppure ricompila il libro.

L'ordine di caricamento dell'indice di ricerca è importante e sensibile ai costi:

1. Carica ogni indice di ricerca specifico per la lingua e di fallback dal repository GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Solo se tutti i candidati ospitati su GitHub falliscono, usa come fallback l'output mdBook della stessa origine.

Non posizionare il fallback locale `/searchindex.js` prima di un qualsiasi fallback ospitato su GitHub, come `searchindex-cloud-en.js.gz`. Servire `searchindex.js` da `cloud.hacktricks.wiki` in produzione è costoso.

Per questo repository, il fallback locale previsto è:

`/searchindex.js`

Il fallback del libro principale per questo repository è:

`/searchindex-book.js`

Questo file è solo un fallback. La fonte primaria deve rimanere costituita dai file remoti `searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex`.

## Pubblicazione dell'indice di ricerca

I workflow che pubblicano gli indici di ricerca compressi e crittografati in `HackTricks-wiki/hacktricks-searchindex` sono:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Il file sorgente generato è `book/searchindex.js`. I nomi degli artifact remoti pubblicati sono:

- `searchindex-cloud-v2-en.json.gz` (indice compatto preferito)
- `searchindex-cloud-v2-<lang>.json.gz` (indice compatto preferito)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Il loader del browser preferisce l'artifact compatto v2 e mantiene l'artifact `.js.gz` come fallback legacy. Entrambi sono payload gzip crittografati con XOR utilizzando la chiave definita in `theme/ht_searcher.js`.

## Compilazione e validazione

Controlli locali comuni:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` fallisce, controlla:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Note sulle modifiche

- Preferisci `rg` per le ricerche.
- Mantieni l'output `book/` generato fuori dai commit, salvo esplicita richiesta. Le correzioni del loader di ricerca fanno eccezione quando le pagine già compilate devono essere corrette immediatamente.
- Se modifichi il comportamento condiviso del tema, confronta e aggiorna il file corrispondente in
`/Users/carlospolop/git/hacktricks`.
- Non annullare modifiche locali non correlate.
