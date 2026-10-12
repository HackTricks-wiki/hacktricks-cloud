# Ścieżki eskalacji uprawnień

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud utrzymuje katalog eskalacji uprawnień w formacie czytelnym maszynowo, z którego korzysta [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Każda technika określa, jakie uprawnienia musi efektywnie posiadać podmiot i do jakich zasobów, aby uzyskać uprawnienia zestawu docelowych podmiotów. Blue-CloudPEASS analizuje te wpisy offline na podstawie migawki inwentaryzacji tylko do odczytu i przedstawia ścieżki ataku między podmiotami, wskazując przyznającą politykę lub powiązanie jako dowód oraz środek zaradczy usuwający daną ścieżkę. Edytuj tutaj pliki kanoniczne, a nie ich kopie w projekcie korzystającym z tego katalogu.

Wpisy opisują wyłącznie warunki wstępne, osiągalne cele i środki zaradcze. Nie zawierają poleceń, payloadów ani instrukcji wykonania; technikę wyjaśnia powiązana strona HackTricks.

## Układ

Dla każdej platformy (`aws`, `gcp`, `azure`, `k8s`) istnieje jeden katalog, a dla każdej usługi — jeden plik `<service>.yaml`, zawierający listę technik w formacie YAML. Pliki o nazwach `_excluded*.yaml` wymieniają przeanalizowane techniki HackTricks, dla których celowo nie utworzono wpisu, na przykład ze względu na post-exploitation, persistence lub brak możliwości modelowania na podstawie konfiguracji; podają też przyczynę. `privesc-technique.schema.json` to wyeksportowany JSON Schema służący do uzupełniania i walidacji w edytorze.

## Pola techniki

- `id`: globalnie unikalny identyfikator, zapisany małymi literami w formacie kebab-case i poprzedzony nazwą platformy.
- `provider`, `service`, `title` i `summary`: jedno zdanie opisujące, co uzyskuje źródło.
- `source`: strona HackTricks i kotwica dokumentujące technikę, podane jako ścieżka względna względem tego repozytorium. `source_revision` to commit książki, który został sprawdzony.
- `requires`: uprawnienia, które musi posiadać źródło. `all_of` zawiera wszystkie wymagane elementy, a `any_of` — alternatywy. Elementy AWS i GCP używają `action` i `resource`, elementy Azure — `action` (lub `data_action`) i `scope`, elementy Entra ID — `entra_permission` lub `entra_role`, a elementy Kubernetes — `verb`, `resource`, `subresource`, `api_group` i `namespace`. Wartości zastępcze, takie jak `{target.arn}`, wiążą wymaganie z celem.
- `target`: `kind` celu, `selector`, którego warunki muszą być spełnione, aby podmiot był osiągalny, oraz jego `scope`.
- `conditions` i `blockers`: czynniki, które mogą w praktyce uniemożliwić wykorzystanie ścieżki, takie jak klucze warunków, SCP, granice uprawnień lub polityki admission.
- `confidence`, `severity`, `mitigation`, `references` oraz opcjonalne `notes`.

Nieznane pola, rodzaje celów, klucze selektora i wartości zastępcze są odrzucane, a nie ignorowane. Dzięki temu wpis nie może po cichu rozszerzyć ani zawęzić zbioru celów. Najpierw dodaj obsługę nowego selektora do ewaluatora po stronie projektu korzystającego z katalogu.

### Połączenia w schemacie v2

Loader v2 dodaje dwie wartości zastępcze i jeden selektor AWS, a także dopuszcza istniejący selektor K8s dla uruchomionych podów w celach GCP. Te pola wymagają dokładnego dopasowania do zebranej inwentaryzacji; brak danych inwentaryzacyjnych oznacza nieznany zakres pokrycia, a nie osiągalną ścieżkę.

| Pole | Zastosowanie i wymagany kształt |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` i `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Używaj ich razem dla celu AWS `aws_account_admin`. Każda alternatywa wymagań musi obejmować `iam:CreatePolicyVersion` dla tej wartości zastępczej. Polityka musi być dołączona do roli, którą źródło może przejąć na tym samym koncie; ewaluator sprawdza dostępność miejsca na nową wersję polityki i ponownie oblicza efektywne uprawnienia roli. `SetDefaultPolicyVersion` nie jest obsługiwane. |
| `target.selector.k8s_sa_used_by_running_pod: true` | W przypadku celu GCP `k8s_service_account` z `scope: cluster` wybiera KSA używane przez uruchomione pody z dostępnym tokenem w dopasowanym klastrze GKE. Nie łącz tego selektora z `k8s_sa_in_cluster` ani `k8s_sa_has_token_secret`. Sposób użycia w K8s pozostaje bez zmian. |
| `{source_rolebound_clusterrole}` | Używaj jako `resource_name` w wymaganiach K8s dotyczących `clusterroles`, z `api_group: rbac.authorization.k8s.io` i `namespace: "*"`. Każda alternatywa wymaga `escalate` oraz `update` lub `patch` dla tej samej nazwy. Celem musi być `k8s_service_account` z `scope: same_namespace` i `selector.k8s_sa_in_namespace: "{target.namespace}"`; RoleBinding musi wiązać źródło w tej przestrzeni nazw. |

## Walidacja i synchronizacja

Przed przesłaniem zmian uruchom `python scripts/validate_privesc_paths.py --book-root .` przy zainstalowanym PyYAML. Skrypt sprawdza układ katalogów, każdy wpis za pomocą rygorystycznego loadera ewaluatora (`scripts/privesc_paths_schema.py`, czyli kopii modułu schematu Blue-CloudPEASS), unikalność identyfikatorów, strony źródłowe i kotwice nagłówków oraz aktualność JSON Schema. Użyj `--peaso-root /path/to/Blue-CloudPEASS`, aby dodatkowo porównać oba pliki schematu bajt po bajcie z wersją w projekcie korzystającym z katalogu. Workflow pull requestów w tym repozytorium uruchamia tę samą walidację.

W każdy poniedziałek Blue-CloudPEASS pobiera aktualną wersję `master` tego repozytorium, waliduje te pliki i porównuje sumę SHA-256 każdego z nich z sumą zapisaną podczas poprzedniej synchronizacji. Dodane, zaktualizowane i usunięte pliki z repozytorium zastępują niezmienione kopie w projekcie korzystającym z katalogu. Zmiana pliku po obu stronach jest zgłaszana jako konflikt, a identyfikatory technik nigdy nie są usuwane bez jawnego, sprawdzonego rejestru. Nieprawidłowa zawartość lub nieudany test nie zmieniają domyślnej gałęzi projektu korzystającego z katalogu. Niezwiązane zmiany w repozytorium nie powodują utworzenia commitu w projekcie korzystającym z katalogu.

{{#include ../banners/hacktricks-training.md}}
