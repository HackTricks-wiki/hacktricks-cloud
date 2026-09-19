# AGENTS.md

Wskazówki dla przyszłych agentów pracujących w tym repozytorium.

## Kontekst repozytorium

To repozytorium HackTricks Cloud mdBook. Powiązana główna książka znajduje się w:

`/Users/carlospolop/git/hacktricks`

Zmiany dotyczące wspólnego theme/search behavior często trzeba zastosować w obu repozytoriach.

## Kontrakt ładowania Search Index

Niestandardowy interfejs search znajduje się w:

`theme/ht_searcher.js`

Może również istnieć wygenerowana kopia w:

`book/theme/ht_searcher.js`

Jeśli production wdraża już zbudowany katalog `book/`, zaktualizuj obie kopie albo przebuduj
book przed deploymentem.

Kolejność ładowania search index jest istotna i kosztowa:

1. Załaduj każdy language-specific i fallback search index z repozytorium GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Dopiero jeśli wszystkie candidates hostowane na GitHub zawiodą, użyj fallbacku do outputu mdBook
   z tego samego origin.

Nie umieszczaj lokalnego fallbacku `/searchindex.js` przed żadnym fallbackiem hostowanym na GitHub,
takim jak `searchindex-cloud-en.js.gz`. Serwowanie `searchindex.js` z `cloud.hacktricks.wiki` w production
jest kosztowne.

Dla tego repo oczekiwany lokalny fallback to:

`/searchindex.js`

Fallbackiem głównej książki dla tego repo jest:

`/searchindex-book.js`

Ten plik jest wyłącznie fallbackiem. Primary source musi pozostać zdalnymi plikami
`searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` w
`HackTricks-wiki/hacktricks-searchindex`.

## Publikowanie Search Index

Workflowy publikujące encrypted compressed search indexes do `HackTricks-wiki/hacktricks-searchindex` to:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Wygenerowany source file to `book/searchindex.js`. Nazwy publikowanych remote artifacts to:

- `searchindex-cloud-v2-en.json.gz` (preferowany compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferowany compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader preferuje compact v2 artifact i zachowuje artifact `.js.gz` jako legacy
fallback. Oba są XOR-encrypted gzip payloads wykorzystującymi key zdefiniowany w
`theme/ht_searcher.js`.

Loader musi pozostać lazy: standardowa nawigacja po stronach nie może tworzyć search workera ani pobierać
indexu, dopóki visitor nie otworzy ani nie użyje search. Zdalne compressed responses są przechowywane w Cache
Storage przez 24 godziny dla każdego origin, aby kolejne strony mogły ich ponownie użyć. Zachowaj
stale-cache fallback, gdy odświeżenie wygasłego entry zawiedzie.

## Build And Validation

Typowe lokalne checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Jeśli `mdbook build` zawiedzie, sprawdź:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Preferuj `rg` do wyszukiwania.
- Nie dodawaj wygenerowanego outputu `book/` do commitów, chyba że wyraźnie o to poproszono. Search loader fixes
  są wyjątkiem, gdy już zbudowane strony muszą zostać natychmiast poprawione.
- Jeśli zmieniasz zachowanie wspólnego theme, porównaj i zaktualizuj odpowiedni plik w
  `/Users/carlospolop/git/hacktricks`.
- Nie cofaj niezwiązanych zmian lokalnych.
