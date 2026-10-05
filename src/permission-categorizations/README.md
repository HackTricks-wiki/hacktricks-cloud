# Kategoryzacje ryzyka uprawnień

HackTricks Cloud utrzymuje współdzielone dane o poziomach ważności uprawnień wykorzystywane przez [CloudPEASS](https://github.com/peass-ng/CloudPEASS) i [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edytuj tutaj kanoniczny plik platformy zamiast wygenerowanych kopii w którymkolwiek z tych konsumentów.

- **Critical**: uprawnienia, które bezpośrednio lub niemal niezależnie przyznają potężne uprawnienia, tworzą tożsamość lub umożliwiają uprzywilejowane wykonanie.
- **High**: dostęp do poufnych informacji, danych uwierzytelniających lub warunkowej ścieżki eskalacji uprawnień.
- **Medium**: DoS/Break, zakłócenia operacyjne, zwykłe zmiany lub warunkowe możliwości bez wykazanej ścieżki do poufnych danych albo uprawnień.
- **Low**: zwykłe rozpoznanie i dostęp do metadanych.

Dla każdej platformy istnieje jeden kanoniczny plik YAML: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) i [Kubernetes](k8s.yaml). Są to pliki czytelne maszynowo; strony platform wyświetlają w przeglądarce kompletny YAML i wyjaśniają, jak go edytować. Wbudowana przeglądarka używa kopii z książki, natomiast workflow PEASS pobiera kanoniczne pliki z GitHub.

## Pliki dostawców chmurowych

`version` i `provider` identyfikują schemat. `permission_categories` zawiera cztery osobne listy uprawnień. Przenieś uprawnienie między listami, aby zmienić jego ocenę. Dopasowanie AWS i Azure ignoruje wielkość liter; dopasowanie GCP zachowuje wielkość liter. Aliasy różniące się wielkością liter mogą się powtarzać w ramach tego samego poziomu ważności, ale sprzeczne oceny są odrzucane.

`severity_overrides` zawiera poddane audytowi wyjątki od reguł ogólnych. Jeśli wyjątek występuje również w katalogu, oba wpisy muszą być zgodne. `severity_caps` uniemożliwia kombinacji podniesienie poziomu wybranych uprawnień. `non_permission_identifiers` wyklucza udokumentowane nazwy metod API, klucze warunków i inne ciągi, które nie są rzeczywistymi uprawnieniami autoryzacyjnymi.

`combinations.critical` i `combinations.high` to listy list uprawnień: każdy element wewnętrznej listy musi zostać przyznany, aby dana kombinacja miała zastosowanie. Zachowaj kombinacje razem; rozdzielenie ich na pojedyncze przyznania zawyżyłoby ryzyko. Istniejące pola dokładnego dopasowania i wyrażeń regularnych nadal pełnią funkcję mechanizmu awaryjnego dla uprawnień nieobecnych w katalogu. Pełne przepisanie klasyfikatora lub nowe zachowanie dopasowywania nadal wymaga zmian w kodzie konsumentów.

## Plik Kubernetes

`rules` jest uporządkowane: wygrywa pierwsza pasująca reguła. Każda reguła ma unikalne `id`, `match`, `severity` i zrozumiały opis w polu `description`. Dodaj bardziej szczegółową regułę przed szerszą albo zmień poziom ważności istniejącej reguły. Zachowaj końcowy bezwarunkowy fallback.

Dopasowania używają `all`, `any` i `not` do tworzenia złożeń albo porównania `field`, `op` i `value`. Dostępne pola to `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (pisany małymi literami URL zasobu), `non_resource_url`, `mode` i `delegated_verb`. Dostępne operacje to `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` i `truthy` (bez wymaganego `value`). `always: true` pasuje do wszystkiego. Wartości group, resource, subresource i verb są pisane małymi literami. Dosłowny wildcard zapisuje się jako `'*'`; dopasowanie przyznania z wildcardem jest jawnie określone w regułach, a nie realizowane przez rozwijanie wzorców powłoki.

`severity_when` opcjonalnie wybiera inny poziom ważności dla pasującego warunku. `severity: delegated` jest zarezerwowane dla ograniczonego impersonation: jego mapa `delegated_severities` przekształca klasyfikację delegowanej akcji w ocenę warunkową. Placeholdery w opisach mogą odwoływać się do dostępnych pól, takich jak `{full}` i `{verb}`. Reguły są danymi i nigdy nie są wykonywane jako kod Python ani shell.

## Walidacja i synchronizacja

Przed przesłaniem zmian uruchom `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` z zainstalowanym PyYAML. Workflow pull requestów książki uruchamia tę samą walidację.

W każdy poniedziałek oba repozytoria konsumentów pobierają bieżący `master` tej książki, walidują wszystkie cztery pliki, porównują hashe SHA-256 i aktualizują dołączone pliki YAML oraz wygenerowane starsze listy. Manifest źródłowy zapisuje rewizję książki i hash każdego pliku. Niezwiązane zmiany w książce nie powodują utworzenia commita u konsumenta. Każdy workflow obsługuje również uruchomienie ręczne. Testy są wykonywane przed zapisaniem przez workflow zmienionych danych do domyślnej gałęzi konsumenta; niepowodzenie pozostawia tę gałąź bez zmian. Pomiędzy aktualizacjami konsumenty nadal używają swoich dołączonych kopii offline.

Aby zaktualizować dane lokalnie u konsumenta, uruchom `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Dodaj `--check`, aby wykryć nieaktualne kopie bez ich zapisywania.

Pobieranie źródeł w obu konsumentach ponawia próbę pięć razy, korzystając z ograniczonych czasowo checkoutów i rosnących opóźnień. Niekompletne pobrania pozostają w katalogach tymczasowych; po wyczerpaniu prób istniejące dołączone dane pozostają niezmienione.
