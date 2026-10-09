# Kategorisierung von Berechtigungsrisiken

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud verwaltet die gemeinsamen Daten zum Schweregrad von Berechtigungen, die von [CloudPEASS](https://github.com/peass-ng/CloudPEASS) und [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) verwendet werden. Bearbeite die kanonische Plattformdatei hier und nicht die generierten Kopien in den beiden verwendenden Repositories.

- **Critical**: Berechtigungen, die direkt oder nahezu eigenständig mächtige Privilegien gewähren, eine Identität erzeugen oder privilegierte Ausführung ermöglichen.
- **High**: Zugriff auf sensible Informationen oder Zugangsdaten oder ein bedingter Pfad zur Rechteausweitung.
- **Medium**: DoS/Break, Betriebsunterbrechungen, gewöhnliche Änderungen oder bedingte Fähigkeiten ohne nachgewiesenen Pfad zu sensiblen Daten oder Privilegien.
- **Low**: gewöhnliche Erkundung und Zugriff auf Metadaten.

Pro Plattform gibt es eine kanonische YAML-Datei: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) und [Kubernetes](k8s.yaml). Diese Dateien sind maschinenlesbar; die Plattformseiten zeigen ihr vollständiges YAML im Browser an und erläutern, wie sie bearbeitet werden. Die Inline-Ansicht verwendet die Kopie des Buchs, während die PEASS-Workflows die kanonischen Dateien von GitHub abrufen.

## Dateien der Cloud-Anbieter

`version` und `provider` identifizieren das Schema. `permission_categories` enthält die vier einzelnen Berechtigungslisten. Verschiebe eine Berechtigung zwischen den Listen, um ihre Einstufung zu ändern. Beim Abgleich von AWS und Azure wird die Groß-/Kleinschreibung ignoriert; beim Abgleich von GCP bleibt sie erhalten. Schreibvarianten mit unterschiedlicher Groß-/Kleinschreibung dürfen innerhalb desselben Schweregrads wiederholt vorkommen, aber widersprüchliche Einstufungen werden abgelehnt.

`severity_overrides` enthält geprüfte Ausnahmen von allgemeinen Regeln. Wenn eine Ausnahme auch im Katalog vorkommt, müssen beide Einträge übereinstimmen. `severity_caps` verhindert, dass eine Kombination bestimmte Berechtigungen höher einstuft. `non_permission_identifiers` schließt dokumentierte API-Methodennamen, Bedingungsschlüssel und andere Zeichenfolgen aus, die keine tatsächlichen Autorisierungsberechtigungen sind.

`combinations.critical` und `combinations.high` sind Listen von Berechtigungslisten: Für eine Kombination müssen alle Elemente einer inneren Liste gewährt sein. Lasse Kombinationen zusammen; eine Aufteilung in einzelne Berechtigungen würde das Risiko überbewerten. Bestehende Felder für exakte Übereinstimmungen und reguläre Ausdrücke dienen weiterhin als Fallback für Berechtigungen, die nicht im Katalog enthalten sind. Eine vollständige Neufassung des Classifiers oder ein neues Abgleichverhalten erfordert weiterhin Codeänderungen in den verwendenden Repositories.

## Kubernetes-Datei

`rules` ist geordnet: Es gilt die erste passende Regel. Jede Regel hat eine eindeutige `id`, ein `match`, einen `severity`-Wert und eine Klartextbeschreibung in `description`. Füge eine spezifischere Regel vor einer allgemeineren ein oder ändere den Schweregrad einer bestehenden Regel. Behalte den abschließenden bedingungslosen Fallback bei.

Für die Zusammensetzung von Bedingungen verwenden Matches `all`, `any` und `not` oder einen Vergleich aus `field`, `op` und `value`. Verfügbare Felder sind `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (kleingeschriebene Nicht-Ressourcen-URL), `non_resource_url`, `mode` und `delegated_verb`. Verfügbare Operationen sind `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` und `truthy` (benötigt keinen Wert). `always: true` trifft auf alles zu. Werte für group, resource, subresource und verb werden kleingeschrieben. Ein wörtlicher Platzhalter wird als `'*'` geschrieben; die Übereinstimmung mit einer Platzhalterberechtigung wird explizit in den Regeln festgelegt und nicht durch Shell-Pattern-Expansion erzielt.

`severity_when` wählt optional für eine passende Bedingung einen anderen Schweregrad aus. `severity: delegated` ist für eingeschränkte Impersonation reserviert: Die Zuordnung `delegated_severities` wandelt die Einstufung der delegierten Aktion in die bedingte Einstufung um. Platzhalter in Beschreibungen können auf die verfügbaren Felder verweisen, etwa `{full}` und `{verb}`. Die Regeln sind Daten und werden niemals als Python- oder Shell-Code ausgeführt.

## Validierung und Synchronisierung

Führe vor dem Einreichen von Änderungen `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` aus, nachdem PyYAML installiert wurde. Der Pull-Request-Workflow des Buchs führt dieselbe Validierung aus.

Jeden Montag checken beide verwendenden Repositories den aktuellen `master`-Branch dieses Buchs aus, validieren alle vier Dateien, vergleichen SHA-256-Hashes und aktualisieren ihre gebündelten YAML-Dateien sowie die generierten Legacy-Listen. Ein Quellmanifest hält die Revision des Buchs und den Hash jeder Datei fest. Nicht damit zusammenhängende Änderungen am Buch führen zu keinem Commit in den verwendenden Repositories. Jeder Workflow unterstützt außerdem einen manuellen Start. Die Tests laufen, bevor der Workflow geänderte Daten in den Standardbranch des verwendenden Repositorys committet; bei Fehlern bleibt dieser Branch unverändert. Zwischen den Aktualisierungen verwenden die Repositories ihre gebündelten Kopien weiterhin offline.

Um die Daten lokal in einem verwendenden Repository zu aktualisieren, führe `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` aus. Füge `--check` hinzu, um veraltete Kopien zu erkennen, ohne sie zu ändern.

Das Abrufen der Quelldateien wird in beiden verwendenden Repositories fünfmal wiederholt, mit begrenzten Checkout-Fristen und zunehmenden Verzögerungen. Unvollständige Downloads verbleiben in temporären Verzeichnissen; sind alle Wiederholungsversuche ausgeschöpft, bleiben die vorhandenen gebündelten Daten unverändert.
{{#include ../banners/hacktricks-training.md}}
