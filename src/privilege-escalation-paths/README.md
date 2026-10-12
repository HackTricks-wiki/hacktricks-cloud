# Privilege escalation paths

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud verwaltet den maschinenlesbaren Katalog für Privilege Escalation, den [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) verwendet. Jede Technik gibt an, über welche Berechtigungen ein Principal effektiv verfügen muss und auf welchen Ressourcen, um die Berechtigungen einer Gruppe von Ziel-Principals zu erlangen. Blue-CloudPEASS wertet diese Einträge offline anhand eines schreibgeschützten Inventory-Snapshots aus und zeichnet Angriffspfade zwischen Principals, wobei die gewährende Policy oder Bindung als Nachweis und die Maßnahme zur Beseitigung des Pfads angezeigt wird. Bearbeite hier die kanonischen Dateien statt der Kopien im Consumer.

Einträge beschreiben nur Voraussetzungen, erreichbare Ziele und Maßnahmen. Sie enthalten keine Befehle, Payloads oder Ausführungsschritte; die verlinkte HackTricks-Seite erläutert die Technik.

## Struktur

Es gibt ein Verzeichnis pro Plattform (`aws`, `gcp`, `azure`, `k8s`) und eine Datei `<service>.yaml` pro Service, die jeweils eine YAML-Liste mit Techniken enthalten. Dateien mit dem Namen `_excluded*.yaml` listen überprüfte HackTricks-Techniken auf, für die es absichtlich keinen Eintrag gibt, etwa Post-Exploitation-, Persistence- oder Techniken, die sich nicht anhand der Konfiguration modellieren lassen, jeweils mit Begründung. `privesc-technique.schema.json` ist das exportierte JSON Schema für Editor-Vervollständigung und Validierung.

## Technikfelder

- `id`: global eindeutig, kleingeschrieben und in kebab-case, mit dem Plattformpräfix.
- `provider`, `service`, `title` und `summary`: jeweils ein Satz, der beschreibt, was die Quelle erlangt.
- `source`: die HackTricks-Seite und der Anker, die die Technik dokumentieren, relativ zu diesem Buch. `source_revision` ist der gelesene Buch-Commit.
- `requires`: die Berechtigungen, über die die Quelle verfügen muss. `all_of` listet alle erforderlichen Einträge auf, `any_of` listet Alternativen auf. AWS- und GCP-Einträge verwenden `action` und `resource`, Azure-Einträge verwenden `action` (oder `data_action`) und `scope`, Entra-ID-Einträge verwenden `entra_permission` oder `entra_role`, und Kubernetes-Einträge verwenden `verb`, `resource`, `subresource`, `api_group` und `namespace`. Platzhalter wie `{target.arn}` binden eine Anforderung an das Ziel.
- `target`: der `kind` des Ziels, ein `selector`, dessen Bedingungen alle erfüllt sein müssen, damit ein Principal erreichbar ist, und dessen `scope`.
- `conditions` und `blockers`: Faktoren, die den Pfad in der Praxis verhindern können, etwa Condition Keys, SCPs, Boundaries oder Admission Policies.
- `confidence`, `severity`, `mitigation`, `references` und optionale `notes`.

Unbekannte Felder, Zieltypen, Selector-Schlüssel und Platzhalter werden zurückgewiesen, nicht ignoriert. Ein Eintrag kann seine Zielmenge also niemals unbemerkt erweitern oder einschränken. Füge Unterstützung für einen neuen Selector zuerst im Consumer-Evaluator hinzu.

### Schema-v2-Joins

Der v2-Loader fügt zwei Platzhalter und einen AWS-Selector hinzu und erlaubt den bestehenden K8s-Selector für laufende Pods bei GCP-Zielen. Diese Felder erfordern einen exakten Abgleich mit dem erfassten Inventory; bei fehlendem Inventory ist die Abdeckung unbekannt, nicht der Pfad erreichbar.

| Feld | Verwendung und erforderliche Form |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` und `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Gemeinsam für ein AWS-Ziel vom Typ `aws_account_admin` verwenden. Jede Anforderungsalternative muss `iam:CreatePolicyVersion` für diesen Platzhalter enthalten. Die Policy muss an eine Rolle angehängt sein, die die Quelle im selben Account annehmen kann; der Evaluator prüft die verfügbare Policy-Versionskapazität und berechnet die effektiven Berechtigungen der Rolle neu. `SetDefaultPolicyVersion` ist nicht abgedeckt. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Für ein GCP-Ziel vom Typ `k8s_service_account` mit `scope: cluster` auswählen; erfasst KSAs, die von laufenden Pods mit verfügbarem Token im abgeglichenen GKE-Cluster verwendet werden. Nicht mit `k8s_sa_in_cluster` oder `k8s_sa_has_token_secret` kombinieren. Die bestehende K8s-Verwendung bleibt unverändert. |
| `{source_rolebound_clusterrole}` | Als `resource_name` für K8s-`clusterroles`-Anforderungen mit `api_group: rbac.authorization.k8s.io` und `namespace: "*"` verwenden. Jede Alternative benötigt `escalate` und `update` oder `patch` für denselben Namen. Das Ziel muss ein `k8s_service_account` mit `scope: same_namespace` und `selector.k8s_sa_in_namespace: "{target.namespace}"` sein; ein RoleBinding muss die Quelle in diesem Namespace binden. |

## Validierung und Synchronisierung

Führe vor dem Einreichen von Änderungen `python scripts/validate_privesc_paths.py --book-root .` mit installiertem PyYAML aus. Das Skript prüft die Verzeichnisstruktur, jeden Eintrag mit dem strikten Loader des Evaluators (`scripts/privesc_paths_schema.py`, einer Kopie des Blue-CloudPEASS-Schema-Moduls), eindeutige IDs, Quellseiten und Überschriftenanker sowie, ob das JSON Schema aktuell ist. Verwende `--peaso-root /path/to/Blue-CloudPEASS`, um zusätzlich beide Schemadateien byteweise mit dem Consumer abzugleichen. Der Pull-Request-Workflow des Buchs führt dieselbe Validierung aus.

Jeden Montag checkt Blue-CloudPEASS den aktuellen `master` dieses Buchs aus, validiert diese Dateien und vergleicht den SHA-256-Hash jeder Datei mit den beim letzten Abgleich gespeicherten Hashes. Upstream hinzugefügte, aktualisierte und gelöschte Dateien ersetzen unveränderte Consumer-Kopien. Eine Datei, die auf beiden Seiten geändert wurde, wird als Konflikt gemeldet; Technik-IDs werden niemals ohne ein ausdrücklich geprüftes Ledger entfernt. Ungültige Inhalte oder ein fehlgeschlagener Test lassen den Default-Branch des Consumers unverändert. Nicht damit zusammenhängende Änderungen am Buch führen zu keinem Commit im Consumer.
{{#include ../banners/hacktricks-training.md}}
