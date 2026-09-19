# AGENTS.md

Indicazioni per i futuri agent che lavorano in questo repository.

## Contesto del repository

Questo è il repository mdBook di HackTricks Cloud. Il libro principale correlato si trova in:

`/Users/carlospolop/git/hacktricks`

Le modifiche al comportamento condiviso di theme/search spesso devono essere applicate in entrambi i repository.

## Contratto di caricamento dell'indice di ricerca

La UI di ricerca personalizzata si trova in:

`theme/ht_searcher.js`

Potrebbe esistere anche una copia generata in:

`book/theme/ht_searcher.js`

Se la produzione esegue il deploy della directory `book/` già compilata, aggiorna entrambe le copie o ricompila il
book prima del deploy.

La policy della sorgente dell'indice di ricerca è importante e sensibile ai costi:

- Sugli host pubblici, carica ogni candidato specifico per la lingua e di fallback esclusivamente da
`HackTricks-wiki/hacktricks-searchindex`. Non usare mai come fallback l'output mdBook della stessa origine;
servire il grande indice da `cloud.hacktricks.wiki` in produzione è costoso.
- Su localhost, sugli host `.local`/`.internal`, sul loopback, sulle reti RFC1918, sul carrier-grade NAT, sugli
indirizzi link-local o sugli indirizzi IPv6 privati, carica solo l'output mdBook della stessa origine, così
i deploy locali/in container rimangono autosufficienti.

Per questo repository, il fallback locale previsto è:

`/searchindex.js`

Il fallback del libro principale per questo repository è:

`/searchindex-book.js`

Questi file locali sono sorgenti esclusivamente per reti private. Gli host pubblici devono usare soltanto i file
remoti `searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex`.

## Pubblicazione dell'indice di ricerca

I workflow che pubblicano gli indici di ricerca compressi e cifrati su
`HackTricks-wiki/hacktricks-searchindex` sono:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Il file sorgente generato è `book/searchindex.js`. I nomi degli artifact remoti pubblicati sono:

- `searchindex-cloud-v2-en.json.gz` (indice compatto preferito)
- `searchindex-cloud-v2-<lang>.json.gz` (indice compatto preferito)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Il browser loader preferisce l'artifact compatto v2 e mantiene l'artifact `.js.gz` come fallback legacy. Entrambi
sono payload gzip cifrati con XOR usando la chiave definita in `theme/ht_searcher.js`.

Il loader deve rimanere lazy: la normale navigazione delle pagine non deve creare il search worker né scaricare un
indice finché il visitatore non apre o utilizza la ricerca. Le risposte remote compresse vengono persistite nella
Cache Storage per 24 ore per origine, così le pagine successive possono riutilizzarle. Mantieni il fallback alla
cache obsoleta quando l'aggiornamento di una voce scaduta non riesce.

## Build e validazione

Controlli locali comuni:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` fallisce, controlla:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Note sulle modifiche

- Preferisci `rg` per le ricerche.
- Mantieni l'output `book/` generato fuori dai commit, salvo richiesta esplicita. Le correzioni al search loader
  fanno eccezione quando le pagine già compilate devono essere corrette immediatamente.
- Se modifichi il comportamento condiviso di theme, confronta e aggiorna il file corrispondente in
`/Users/carlospolop/git/hacktricks`.
- Non annullare modifiche locali non correlate.
