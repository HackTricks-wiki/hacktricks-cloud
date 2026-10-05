# Kategoryzacje ryzyka uprawnień

HackTricks Cloud utrzymuje współdzielone dane dotyczące poziomu ważności uprawnień, używane przez [CloudPEASS](https://github.com/peass-ng/CloudPEASS) i [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edytuj tutaj kanoniczny plik platformy zamiast wygenerowanych kopii znajdujących się w obu konsumentach.

- **Critical**: uprawnienia, które bezpośrednio lub niemal niezależnie przyznają potężne przywileje, tworzą tożsamość lub umożliwiają uprzywilejowane wykonanie.
- **High**: dostęp do poufnych informacji, poświadczeń lub warunkowej ścieżki eskalacji uprawnień.
- **Medium**: DoS/Break, zakłócenia operacyjne, zwykłe zmiany lub warunkowe możliwości bez wykazanej ścieżki dostępu do poufnych danych albo eskalacji uprawnień.
- **Low**: zwykłe rozpoznanie i dostęp do metadanych.

Dla każdej platformy istnieje jeden kanoniczny plik YAML: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) i [Kubernetes](k8s.yaml). Są to pliki czytelne maszynowo; strony platform wyjaśniają, jak je edytować.

## Pliki dostawców chmurowych

`version` i `provider` identyfikują schemat. `permission_categories` zawiera cztery osobne listy uprawnień. Przenieś uprawnienie między listami, aby zmienić jego ocenę. Dopasowywanie AWS i Azure ignoruje wielkość liter; dopasowywanie GCP zachowuje wielkość liter. Aliasy wielkości liter mogą się powtarzać w ramach tego samego poziomu ważności, ale sprzeczne oceny są odrzucane.

`severity_overrides` zawiera poddane audytowi wyjątki od ogólnych reguł. Jeśli wyjątek występuje również w katalogu, oba wpisy muszą być zgodne. `severity_caps` zapobiega podniesieniu poziomu wybranych uprawnień przez ich kombinację. `non_permission_identifiers` wyklucza udokumentowane nazwy metod API, klucze warunków i inne ciągi, które nie są rzeczywistymi uprawnieniami autoryzacji.

`combinations.critical` i `combinations.high` to listy list uprawnień: aby kombinacja miała zastosowanie, każde uprawnienie z wewnętrznej listy musi zostać przyznane. Zachowaj kombinacje w całości; rozdzielenie ich na pojedyncze przyznania zawyżyłoby ryzyko. Istniejące pola dokładnego dopasowania i wyrażeń regularnych pozostają mechanizmem awaryjnym dla uprawnień nieobecnych w katalogu. Pełne przepisanie klasyfikatora lub dodanie nowego sposobu dopasowywania nadal wymaga zmian w kodzie konsumentów.

## Plik Kubernetes

`rules` jest uporządkowane: wygrywa pierwsza pasująca reguła. Każda reguła ma unikalne `id`, `match`, `severity` i opis w języku naturalnym. Dodaj bardziej szczegółową regułę przed szerszą regułą albo zmień poziom ważności istniejącej reguły. Zachowaj końcowy bezwarunkowy fallback.

Dopasowania używają `all`, `any` i `not` do tworzenia złożeń albo porównania `field`, `op` i `value`. Dostępne pola to `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (małe litery, URL zasobu niebędącego zasobem), `non_resource_url`, `mode` i `delegated_verb`. Dostępne operacje to `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` i `truthy` (nie wymaga wartości). `always: true` dopasowuje wszystko. Wartości group, resource, subresource i verb są zapisane małymi literami. Dosłowny wildcard zapisuje się jako `'*'`; dopasowanie przyznania wildcard jest jawnie określone w regułach, a nie realizowane przez rozwijanie wzorców powłoki.

`severity_when` opcjonalnie wybiera inny poziom ważności dla pasującego warunku. `severity: delegated` jest zarezerwowane dla ograniczonej impersonacji: jego mapa `delegated_severities` przekształca klasyfikację delegowanej akcji w warunkową ocenę. Placeholdery opisu mogą odwoływać się do dostępnych pól, takich jak `{full}` i `{verb}`. Reguły są danymi i nigdy nie są interpretowane jako kod Python ani shell.

## Walidacja i synchronizacja

Przed przesłaniem zmian uruchom `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` z zainstalowanym PyYAML. Workflow pull requestów tej książki uruchamia tę samą walidację.

W każdy poniedziałek oba repozytoria konsumentów pobierają bieżący `master` tej książki, weryfikują wszystkie cztery pliki, porównują hasze SHA-256 oraz aktualizują dołączone pliki YAML i wygenerowane starsze listy. Manifest źródłowy rejestruje rewizję książki i hasz każdego pliku. Niezwiązane zmiany w książce nie powodują utworzenia commita w konsumentach. Każdy workflow obsługuje również uruchomienie ręczne. Testy są wykonywane przed zatwierdzeniem zmienionych danych przez workflow w domyślnej gałęzi konsumenta; niepowodzenia pozostawiają tę gałąź bez zmian. Między aktualizacjami konsumenty nadal używają swoich dołączonych kopii offline.

Aby lokalnie zaktualizować dane w konsumencie, uruchom `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Dodaj `--check`, aby wykryć nieaktualne kopie bez ich zapisywania.
