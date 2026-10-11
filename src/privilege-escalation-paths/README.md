# Ścieżki eskalacji uprawnień

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud utrzymuje czytelny maszynowo katalog eskalacji uprawnień używany przez [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Każda technika określa, jakie uprawnienia musi faktycznie posiadać principal i do jakich zasobów, aby uzyskać uprawnienia zestawu docelowych principals. Blue-CloudPEASS ocenia te wpisy offline na podstawie migawki inwentarza tylko do odczytu i rysuje ścieżki ataku między principals, wskazując przyznającą politykę lub binding jako dowód oraz zabezpieczenie usuwające tę ścieżkę. Edytuj tutaj pliki kanoniczne, a nie ich kopie u odbiorcy.

Wpisy opisują wyłącznie warunki wstępne, osiągalne cele i zabezpieczenie. Nie zawierają poleceń, payloadów ani kroków wykonania; technikę wyjaśnia powiązana strona HackTricks.

## Układ

Dla każdej platformy (`aws`, `gcp`, `azure`, `k8s`) istnieje jeden katalog, a dla każdej usługi jeden plik `<service>.yaml`, zawierający listę technik w formacie YAML. Pliki o nazwach `_excluded*.yaml` zawierają sprawdzone techniki HackTricks, które celowo nie mają wpisu, na przykład techniki post-exploitation, persistence lub techniki, których nie można modelować na podstawie konfiguracji, wraz z uzasadnieniem. `privesc-technique.schema.json` to wyeksportowany JSON Schema używany do podpowiedzi i walidacji w edytorze.

## Pola techniki

- `id`: globalnie unikalny identyfikator, zapisany małymi literami w kebab-case i poprzedzony nazwą platformy.
- `provider`, `service`, `title` i `summary`: jedno zdanie opisujące, co uzyskuje źródło.
- `source`: strona HackTricks i kotwica dokumentujące technikę, podane względem katalogu tej książki. `source_revision` to commit książki, który został przeanalizowany.
- `requires`: uprawnienia, które musi posiadać źródło. `all_of` zawiera wszystkie wymagane elementy, a `any_of` — alternatywy. Elementy AWS i GCP używają `action` i `resource`, elementy Azure — `action` (lub `data_action`) i `scope`, elementy Entra ID — `entra_permission` lub `entra_role`, a elementy Kubernetes — `verb`, `resource`, `subresource`, `api_group` i `namespace`. Wartości zastępcze, takie jak `{target.arn}`, wiążą wymaganie z celem.
- `target`: docelowy `kind`, `selector`, którego wszystkie warunki muszą być spełnione, aby principal był osiągalny, oraz jego `scope`.
- `conditions` i `blockers`: czynniki, które mogą w praktyce uniemożliwić wykorzystanie ścieżki, takie jak klucze warunków, SCP, granice uprawnień lub polityki admission.
- `confidence`, `severity`, `mitigation`, `references` i opcjonalne `notes`.

Nieznane pola, rodzaje celów, klucze selektorów i wartości zastępcze są odrzucane, a nie ignorowane, dzięki czemu wpis nie może po cichu rozszerzyć ani zawęzić zbioru celów. Najpierw dodaj obsługę nowego selektora w ewaluatorze odbiorcy.

## Walidacja i synchronizacja

Przed przesłaniem zmian uruchom `python scripts/validate_privesc_paths.py --book-root .` przy zainstalowanym PyYAML. Skrypt sprawdza układ katalogów, każdy wpis za pomocą ścisłego loadera ewaluatora (`scripts/privesc_paths_schema.py`, kopii modułu schematu Blue-CloudPEASS), unikalność identyfikatorów, istnienie każdej strony `source` w tej książce oraz aktualność JSON Schema. Workflow pull requestów w książce uruchamia tę samą walidację.

W każdy poniedziałek Blue-CloudPEASS pobiera aktualną gałąź `master` tej książki, waliduje te pliki i porównuje sumę SHA-256 każdego pliku z sumami zapisanymi podczas poprzedniej synchronizacji. Dodane, zaktualizowane i usunięte elementy z repozytorium źródłowego zastępują niezmienione kopie u odbiorcy. Plik zmieniony po obu stronach jest zgłaszany jako konflikt, a identyfikatory technik nigdy nie są usuwane bez jawnego, sprawdzonego rejestru. Nieprawidłowa zawartość lub niezaliczony test pozostawia domyślną gałąź odbiorcy bez zmian. Niezwiązane zmiany w książce nie powodują żadnego commita u odbiorcy.
{{#include ../banners/hacktricks-training.md}}
