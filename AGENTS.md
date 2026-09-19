# AGENTS.md

Wskazówki dla przyszłych agentów pracujących w tym repozytorium.

## Kontekst repozytorium

To jest repozytorium mdBook HackTricks Cloud. Powiązana główna książka znajduje się pod adresem:

`/Users/carlospolop/git/hacktricks`

Zmiany dotyczące współdzielonego theme/search behavior często trzeba zastosować w obu repozytoriach.

## Kontrakt ładowania indeksu wyszukiwania

Niestandardowy interfejs wyszukiwania znajduje się w:

`theme/ht_searcher.js`

Może także istnieć wygenerowana kopia w:

`book/theme/ht_searcher.js`

Jeśli produkcja wdraża już zbudowany katalog `book/`, zaktualizuj obie kopie albo przebuduj
book przed wdrożeniem.

Kolejność ładowania indeksu wyszukiwania jest ważna i wrażliwa na koszty:

1. Załaduj każdy language-specific i fallback search index z repozytorium GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Dopiero jeśli wszystkie kandydaty hostowane na GitHub zawiodą, użyj fallback do outputu mdBook z tego samego originu.

Nie umieszczaj lokalnego fallbacku `/searchindex.js` przed jakimkolwiek fallbackiem hostowanym na GitHub, takim jak
`searchindex-cloud-en.js.gz`. Serwowanie `searchindex.js` z `cloud.hacktricks.wiki` w produkcji jest kosztowne.

Dla tego repozytorium oczekiwanym lokalnym fallbackiem jest:

`/searchindex.js`

Fallbackiem głównej książki dla tego repozytorium jest:

`/searchindex-book.js`

Ten plik jest tylko fallbackiem. Głównym źródłem muszą pozostać zdalne pliki
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` w
`HackTricks-wiki/hacktricks-searchindex`.

## Publikowanie indeksu wyszukiwania

Workflowy publikujące zaszyfrowane, skompresowane indeksy wyszukiwania w
`HackTricks-wiki/hacktricks-searchindex` to:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Wygenerowany plik źródłowy to `book/searchindex.js`. Nazwy publikowanych zdalnych artefaktów to:

- `searchindex-cloud-v2-en.json.gz` (preferowany compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferowany compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader preferuje compact v2 artifact i zachowuje artifact `.js.gz` jako legacy fallback. Oba są payloadami gzip zaszyfrowanymi XOR z użyciem klucza zdefiniowanego w `theme/ht_searcher.js`.

## Budowanie i walidacja

Typowe lokalne sprawdzenia:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Jeśli `mdbook build` zakończy się błędem, sprawdź:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Uwagi dotyczące edycji

- Preferuj `rg` do wyszukiwania.
- Nie dodawaj wygenerowanego outputu `book/` do commitów, chyba że wyraźnie o to poproszono. Poprawki search loadera są wyjątkiem, gdy już zbudowane strony muszą zostać natychmiast poprawione.
- Jeśli zmieniasz zachowanie współdzielonego theme, porównaj i zaktualizuj odpowiadający mu plik w
`/Users/carlospolop/git/hacktricks`.
- Nie wycofuj niezwiązanych lokalnych zmian.
