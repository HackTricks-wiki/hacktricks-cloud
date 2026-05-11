# AGENTS.md

Wytyczne dla przyszłych agentów pracujących w tym repozytorium.

## Kontekst repozytorium

To jest repozytorium HackTricks Cloud mdBook. Powiązana główna książka znajduje się pod adresem:

`/Users/carlospolop/git/hacktricks`

Zmiany we współdzielonym theme/search behavior często trzeba wprowadzić w obu repozytoriach.

## Search Index Loading Contract

Niestandardowy interfejs wyszukiwania znajduje się w:

`theme/ht_searcher.js`

Może też istnieć wygenerowana kopia w:

`book/theme/ht_searcher.js`

Jeśli produkcja wdraża już zbudowany katalog `book/`, zaktualizuj obie kopie albo przebuduj book przed wdrożeniem.

Kolejność ładowania search index jest ważna i wrażliwa kosztowo:

1. Załaduj każdy językowy i fallbackowy search index z repozytorium GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Tylko jeśli wszystkie kandydaty hostowane na GitHub zawiodą, przełącz się na output mdBook z tego samego origin.

Nie umieszczaj lokalnego fallback `/searchindex.js` przed żadnym fallbackiem hostowanym na GitHub, takim jak
`searchindex-cloud-en.js.gz`. Serwowanie `searchindex.js` z `cloud.hacktricks.wiki` w produkcji jest kosztowne.

Dla tego repozytorium oczekiwany lokalny fallback to:

`/searchindex.js`

Fallback głównej książki dla tego repozytorium to:

`/searchindex-book.js`

Ten plik jest tylko fallbackiem. Głównym źródłem muszą pozostać zdalne pliki
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` w
`HackTricks-wiki/hacktricks-searchindex`.

## Search Index Publishing

Workflows publikujące zaszyfrowane skompresowane search indexes do
`HackTricks-wiki/hacktricks-searchindex` to:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Wygenerowany plik źródłowy to `book/searchindex.js`. Nazwy publikowanych zdalnych artefaktów to:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Loader w przeglądarce oczekuje zdalnych plików `.js.gz` będących zaszyfrowanymi XOR payloadami gzip, używając klucza zdefiniowanego w `theme/ht_searcher.js`.

## Build And Validation

Typowe lokalne sprawdzenia:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Jeśli `mdbook build` się nie powiedzie, sprawdź:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Preferuj `rg` do wyszukiwania.
- Trzymaj wygenerowany output `book/` poza commitami, chyba że wyraźnie o to poproszono. Poprawki loadera search są wyjątkiem, gdy już zbudowane strony muszą zostać natychmiast naprawione.
- Jeśli zmieniasz współdzielone zachowanie theme, porównaj i zaktualizuj pasujący plik w
`/Users/carlospolop/git/hacktricks`.
- Nie cofaj niezwiązanych lokalnych zmian.
