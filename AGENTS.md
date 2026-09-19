# AGENTS.md

Wskazówki dla przyszłych agentów pracujących w tym repozytorium.

## Kontekst repozytorium

To jest repozytorium HackTricks Cloud mdBook. Powiązana główna książka znajduje się w:

`/Users/carlospolop/git/hacktricks`

Zmiany dotyczące współdzielonego motywu lub działania wyszukiwania często trzeba zastosować w obu repozytoriach.

## Umowa ładowania indeksu wyszukiwania

Niestandardowy interfejs wyszukiwania znajduje się w:

`theme/ht_searcher.js`

Może również istnieć wygenerowana kopia w:

`book/theme/ht_searcher.js`

Jeśli produkcja wdraża już zbudowany katalog `book/`, zaktualizuj obie kopie albo przebuduj
book przed wdrożeniem.

Polityka źródła indeksu wyszukiwania jest istotna i wrażliwa na koszty:

- Na publicznych hostach każdą kandydacką wersję językową i fallback ładuj wyłącznie z
`HackTricks-wiki/hacktricks-searchindex`. Nigdy nie używaj fallbacku do outputu mdBook z tego samego originu;
serwowanie dużego indeksu z `cloud.hacktricks.wiki` na produkcji jest kosztowne.
- Na hostach localhost, `.local`/`.internal`, loopback, RFC1918, carrier-grade NAT, link-local lub
prywatnych adresach IPv6 ładuj wyłącznie output mdBook z tego samego originu, aby lokalne/w kontenerach wdrożenia
pozostały samowystarczalne.

Dla tego repozytorium oczekiwanym lokalnym fallbackiem jest:

`/searchindex.js`

Fallbackiem głównej książki dla tego repozytorium jest:

`/searchindex-book.js`

Te lokalne pliki są źródłami wyłącznie dla sieci prywatnych. Publiczne hosty muszą używać zdalnych
plików `searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` w
`HackTricks-wiki/hacktricks-searchindex` wyłącznie.

## Publikowanie indeksu wyszukiwania

Workflowy publikujące zaszyfrowane, skompresowane indeksy wyszukiwania do
`HackTricks-wiki/hacktricks-searchindex` to:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Wygenerowany plik źródłowy to `book/searchindex.js`. Nazwy publikowanych zdalnych artefaktów to:

- `searchindex-cloud-v2-en.json.gz` (preferowany kompaktowy indeks)
- `searchindex-cloud-v2-<lang>.json.gz` (preferowany kompaktowy indeks)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Loader przeglądarki preferuje kompaktowy artefakt v2 i zachowuje artefakt `.js.gz` jako
legacy fallback. Oba są payloadami gzip zaszyfrowanymi za pomocą XOR z użyciem klucza zdefiniowanego w `theme/ht_searcher.js`.

Loader musi pozostać lazy: zwykła nawigacja po stronach nie może tworzyć search workera ani pobierać indeksu,
dopóki odwiedzający nie otworzy wyszukiwania lub z niego nie skorzysta. Zdalne skompresowane odpowiedzi są
przechowywane w Cache Storage przez 24 godziny dla każdego originu, dzięki czemu kolejne strony mogą ich używać ponownie.
Zachowaj fallback do nieaktualnego cache podczas odświeżania, jeśli odświeżenie wygasłego wpisu się nie powiedzie.

## Budowanie i walidacja

Typowe lokalne kontrole:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Jeśli `mdbook build` zakończy się błędem, sprawdź:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Uwagi dotyczące edycji

- Do wyszukiwania preferuj `rg`.
- Nie umieszczaj wygenerowanego outputu `book/` w commitach, chyba że wyraźnie o to poproszono. Poprawki search loadera
są wyjątkiem, gdy już zbudowane strony muszą zostać natychmiast poprawione.
- Jeśli zmieniasz działanie współdzielonego motywu, porównaj i zaktualizuj odpowiadający plik w
`/Users/carlospolop/git/hacktricks`.
- Nie cofaj niezwiązanych lokalnych zmian.
