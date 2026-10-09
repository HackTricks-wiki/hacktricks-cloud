# Klasyfikacja ryzyka uprawnień

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud przechowuje wspólne dane o poziomach ważności uprawnień, z których korzystają [CloudPEASS](https://github.com/peass-ng/CloudPEASS) i [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edytuj kanoniczny plik platformy, a nie wygenerowane kopie w którymkolwiek z tych repozytoriów.

- **Critical**: uprawnienia, które bezpośrednio lub niemal samodzielnie przyznają szerokie uprawnienia, tworzą tożsamość lub umożliwiają uprzywilejowane wykonanie.
- **High**: dostęp do poufnych informacji, poświadczeń lub warunkowa ścieżka eskalacji uprawnień.
- **Medium**: DoS/Break, zakłócenia operacyjne, zwykłe zmiany lub warunkowe możliwości bez wykazanej ścieżki do poufnych danych lub uprawnień.
- **Low**: zwykłe rozpoznanie i dostęp do metadanych.

Dla każdej platformy istnieje jeden kanoniczny plik YAML: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) i [Kubernetes](k8s.yaml). Są to pliki czytelne maszynowo; strony platform wyświetlają w przeglądarce ich pełną zawartość YAML i wyjaśniają, jak je edytować. Wbudowana przeglądarka korzysta z kopii z książki, a procesy PEASS pobierają kanoniczne pliki z GitHub.

## Pliki dostawców chmurowych

`version` i `provider` określają schemat. `permission_categories` zawiera cztery osobne listy uprawnień. Przenieś uprawnienie między listami, aby zmienić jego ocenę. Dopasowywanie AWS i Azure nie uwzględnia wielkości liter; dopasowywanie GCP ją uwzględnia. Warianty różniące się wielkością liter mogą powtarzać się w ramach tego samego poziomu ważności, ale sprzeczne oceny są odrzucane.

`severity_overrides` zawiera sprawdzone wyjątki od reguł ogólnych. Jeśli wyjątek występuje również w katalogu, oba wpisy muszą być zgodne. `severity_caps` uniemożliwia kombinacji podniesienie poziomu wybranych uprawnień. `non_permission_identifiers` wyklucza udokumentowane nazwy metod API, klucze warunków i inne ciągi, które nie są rzeczywistymi uprawnieniami autoryzacyjnymi.

`combinations.critical` i `combinations.high` to listy list uprawnień: aby dana kombinacja miała zastosowanie, muszą zostać przyznane wszystkie elementy listy wewnętrznej. Nie rozdzielaj kombinacji; potraktowanie ich elementów jako pojedynczych uprawnień zawyżyłoby ryzyko. Istniejące pola dopasowania dokładnego i wyrażeń regularnych nadal służą jako rozwiązanie zastępcze dla uprawnień spoza katalogu. Pełne przepisanie klasyfikatora lub zmiana sposobu dopasowywania nadal wymaga zmian w kodzie repozytoriów korzystających z tych danych.

## Plik Kubernetes

Kolejność `rules` ma znaczenie: stosowana jest pierwsza pasująca reguła. Każda reguła ma unikalne `id`, `match`, `severity` i opis zrozumiały dla użytkownika. Dodaj bardziej szczegółową regułę przed ogólniejszą albo zmień poziom ważności istniejącej reguły. Zachowaj końcową regułę zastępczą bez warunków.

Dopasowania używają `all`, `any` i `not` do łączenia warunków albo porównania `field`, `op` i `value`. Dostępne pola to `group`, `resource`, `subresource`, `full` (zasób/podzasób), `verb`, `namespace`, `name`, `path` (adres URL zasobu innego niż zasób, zapisany małymi literami), `non_resource_url`, `mode` i `delegated_verb`. Dostępne operacje to `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` i `truthy` (nie wymaga wartości). `always: true` pasuje do wszystkiego. Wartości grupy, zasobu, podzasobu i czasownika są zapisane małymi literami. Dosłowny symbol wieloznaczny zapisuje się jako `'*'`; dopasowanie uprawnienia z symbolem wieloznacznym musi być jawnie określone w regułach, a nie wynikać z rozwijania wzorców powłoki.

Opcjonalne `severity_when` wybiera inny poziom ważności dla pasującego warunku. `severity: delegated` jest zarezerwowane dla ograniczonego podszywania się: jego mapa `delegated_severities` przekształca klasyfikację delegowanej czynności w ocenę warunkową. Wartości zastępcze w opisie mogą odwoływać się do dostępnych pól, takich jak `{full}` i `{verb}`. Reguły są danymi i nigdy nie są wykonywane jako kod Python ani powłoki.

## Walidacja i synchronizacja

Przed przesłaniem zmian uruchom `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` po zainstalowaniu PyYAML. Proces obsługi pull requestów w książce przeprowadza tę samą walidację.

W każdy poniedziałek oba repozytoria korzystające z tych danych pobierają aktualną wersję `master` tej książki, walidują wszystkie cztery pliki, porównują sumy SHA-256 oraz aktualizują dołączone pliki YAML i wygenerowane starsze listy. Manifest źródłowy zapisuje rewizję książki i sumę kontrolną każdego pliku. Niezwiązane zmiany w książce nie powodują utworzenia commita w repozytorium korzystającym z tych danych. Każdy proces obsługuje również ręczne uruchomienie. Testy są uruchamiane przed zatwierdzeniem zmienionych danych w domyślnej gałęzi repozytorium; w razie błędu gałąź pozostaje bez zmian. Między aktualizacjami repozytoria nadal korzystają z dołączonych kopii w trybie offline.

Aby zaktualizować dane lokalnie w repozytorium korzystającym z tych danych, uruchom `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Dodaj `--check`, aby wykryć nieaktualne kopie bez ich zapisywania.

Pobieranie źródeł w obu repozytoriach jest ponawiane pięć razy, z ograniczonym czasem na pobranie i rosnącymi przerwami. Niekompletne pobrania pozostają w katalogach tymczasowych; po wyczerpaniu prób istniejące dołączone dane pozostają bez zmian.
{{#include ../banners/hacktricks-training.md}}
