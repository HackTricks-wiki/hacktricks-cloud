# Privilege-Escalation-Pfade

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud pflegt den maschinenlesbaren Katalog zur Rechteausweitung, den [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) verwendet. Jede Technik gibt an, welche Berechtigungen ein Principal effektiv besitzen muss und auf welchen Ressourcen, um die Berechtigungen einer Gruppe von Ziel-Principals zu erlangen. Blue-CloudPEASS wertet diese Einträge offline anhand eines schreibgeschützten Inventar-Snapshots aus und zeichnet Angriffspfade von Principal zu Principal, mit der gewährenden Richtlinie oder Bindung als Nachweis und der Maßnahme, die den Pfad entfernt. Bearbeite die kanonischen Dateien hier und nicht die Kopien im Consumer.

Einträge beschreiben nur Voraussetzungen, erreichbare Ziele und die Maßnahme. Sie enthalten keine Befehle, Payloads oder Ausführungsschritte; die verlinkte HackTricks-Seite erklärt die Technik.

## Verzeichnisstruktur

Es gibt ein Verzeichnis pro Plattform (`aws`, `gcp`, `azure`, `k8s`) und eine Datei `<service>.yaml` pro Service, die jeweils eine YAML-Liste von Techniken enthalten. Dateien mit dem Namen `_excluded*.yaml` listen geprüfte HackTricks-Techniken auf, für die bewusst kein Eintrag existiert, etwa Post-Exploitation, Persistenz oder Techniken, die sich nicht anhand der Konfiguration modellieren lassen, und nennen den Grund. `privesc-technique.schema.json` ist das exportierte JSON Schema für die Vervollständigung und Validierung im Editor.

## Felder der Techniken

- `id`: global eindeutig, kleingeschrieben und in kebab-case, mit dem Plattformnamen als Präfix.
- `provider`, `service`, `title` und `summary`: ein Satz, der beschreibt, was der Ursprung erlangt.
- `source`: die HackTricks-Seite und der Anker, die die Technik dokumentieren, relativ zu diesem Buch. `source_revision` ist der Commit dieses Buchs, der eingesehen wurde.
- `requires`: die Berechtigungen, die der Ursprung besitzen muss. `all_of` listet alle erforderlichen Elemente auf, `any_of` die Alternativen. AWS- und GCP-Elemente verwenden `action` und `resource`, Azure-Elemente `action` (oder `data_action`) und `scope`, Entra-ID-Elemente `entra_permission` oder `entra_role` und Kubernetes-Elemente `verb`, `resource`, `subresource`, `api_group` und `namespace`. Platzhalter wie `{target.arn}` binden eine Voraussetzung an das Ziel.
- `target`: der `kind` des Ziels, ein `selector`, dessen Bedingungen alle erfüllt sein müssen, damit ein Principal erreichbar ist, und dessen `scope`.
- `conditions` und `blockers`: was den Pfad in der Praxis verhindern kann, etwa Condition Keys, SCPs, Grenzen oder Admission Policies.
- `confidence`, `severity`, `mitigation`, `references` und optionale `notes`.

Unbekannte Felder, Zieltypen, Selector-Schlüssel und Platzhalter werden abgelehnt statt ignoriert, damit ein Eintrag die Menge möglicher Ziele niemals unbemerkt erweitern oder einschränken kann. Füge Unterstützung für einen neuen Selector zuerst im Consumer-Evaluator hinzu.

## Validierung und Synchronisierung

Führe vor dem Einreichen von Änderungen `python scripts/validate_privesc_paths.py --book-root .` aus; PyYAML muss installiert sein. Das Skript prüft die Verzeichnisstruktur, jeden Eintrag mit dem strikten Loader des Evaluators (`scripts/privesc_paths_schema.py`, einer Kopie des Blue-CloudPEASS-Schema-Moduls), eindeutige IDs, das Vorhandensein jeder `source`-Seite in diesem Buch und die Aktualität des JSON Schema. Der Pull-Request-Workflow des Buchs führt dieselbe Validierung aus.

Jeden Montag checkt Blue-CloudPEASS den aktuellen `master` dieses Buchs aus, validiert diese Dateien und vergleicht den SHA-256-Hash jeder Datei mit den Hashes der vorherigen Synchronisierung. Upstream-Hinzufügungen, -Aktualisierungen und -Löschungen ersetzen unveränderte Consumer-Kopien. Änderungen an einer Datei auf beiden Seiten werden als Konflikt gemeldet, und Technik-IDs werden nur mit einem ausdrücklich geprüften Ledger entfernt. Ungültige Inhalte oder ein fehlgeschlagener Test lassen den Standard-Branch des Consumers unverändert. Unabhängige Änderungen am Buch führen zu keinem Commit im Consumer.

{{#include ../banners/hacktricks-training.md}}
