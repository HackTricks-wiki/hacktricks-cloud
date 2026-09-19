# AGENTS.md

Wskazówki dla przyszłych agentów pracujących w tym repozytorium.

## Kontekst repozytorium

To repozytorium HackTricks Cloud mdBook. Powiązana główna książka znajduje się pod adresem:

`/Users/carlospolop/git/hacktricks`

Zmiany dotyczące wspólnego motywu lub zachowania wyszukiwania często trzeba zastosować w obu repozytoriach.

## Kontrakt ładowania indeksu wyszukiwania

Niestandardowy interfejs wyszukiwania znajduje się w:

`theme/ht_searcher.js`

Może również istnieć wygenerowana kopia w:

`book/theme/ht_searcher.js`

Jeśli produkcja wdraża już zbudowany katalog `book/`, zaktualizuj obie kopie albo przebuduj książkę przed wdrożeniem.

Zasady dotyczące źródła indeksu wyszukiwania są istotne i wrażliwe na koszty:

- Na publicznych hostach wszystkie kandydatury specyficzne dla języka oraz fallback należy ładować wyłącznie z `HackTricks-wiki/hacktricks-searchindex`. Nie używaj fallbacku do outputu mdBook z tego samego originu; udostępnianie dużego indeksu z `cloud.hacktricks.wiki` w produkcji jest kosztowne.
- Na localhost, hostach `.local`/`.internal`, adresach loopback, RFC1918, carrier-grade NAT, link-local oraz prywatnych adresach IPv6 ładuj wyłącznie output mdBook z tego samego originu, aby lokalne wdrożenia i wdrożenia kontenerowe pozostały samowystarczalne. Dla strony nieangielskiej najpierw wypróbuj lokalną ścieżkę z prefiksem językowym (na przykład `/es/searchindex.js`), a głównego angielskiego indeksu użyj wyłącznie jako fallbacku.

Dla tego repozytorium oczekiwanym lokalnym fallbackiem jest:

`/searchindex.js`

Fallbackiem głównej książki dla tego repozytorium jest:

`/searchindex-book.js`

Te lokalne pliki są źródłami wyłącznie dla sieci prywatnych. Publiczne hosty muszą korzystać wyłącznie ze zdalnych plików `searchindex-<lang>.js.gz` i `searchindex-cloud-<lang>.js.gz` w `HackTricks-wiki/hacktricks-searchindex`.

## Publikowanie indeksu wyszukiwania

Workflowy publikujące zaszyfrowane, skompresowane indeksy wyszukiwania w `HackTricks-wiki/hacktricks-searchindex` to:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Wygenerowany plik źródłowy to `book/searchindex.js`. Nazwy publikowanych zdalnych artefaktów to:

- `searchindex-cloud-v2-en.json.gz` (preferowany kompaktowy indeks)
- `searchindex-cloud-v2-<lang>.json.gz` (preferowany kompaktowy indeks)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader preferuje artefakt v2 w formacie compact i zachowuje artefakt `.js.gz` jako legacy fallback. Oba są zaszyfrowanymi payloadami gzip z użyciem klucza zdefiniowanego w `theme/ht_searcher.js`.

Loader musi pozostać lazy: zwykła nawigacja po stronach nie może tworzyć search workera ani pobierać indeksu, dopóki odwiedzający nie otworzy wyszukiwania lub z niego nie skorzysta. Zdalne skompresowane odpowiedzi są przechowywane w Cache Storage przez 24 godziny dla każdego originu, dzięki czemu kolejne strony mogą z nich korzystać. Zachowaj fallback do nieaktualnego cache'a, gdy odświeżenie wygasłego wpisu się nie powiedzie.

## Budowanie i walidacja

Typowe lokalne kontrole:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Jeśli `mdbook build` zakończy się błędem, sprawdź:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Uwagi dotyczące edycji

- Do wyszukiwania preferuj `rg`.
- Nie umieszczaj wygenerowanego outputu `book/` w commitach, chyba że wyraźnie o to poproszono. Wyjątkiem są poprawki search loadera, gdy już zbudowane strony muszą zostać natychmiast poprawione.
- Jeśli zmieniasz zachowanie wspólnego motywu, porównaj i zaktualizuj odpowiedni plik w `/Users/carlospolop/git/hacktricks`.
- Nie wycofuj niezwiązanych zmian lokalnych.
