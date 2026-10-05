# Kategorisierungen von Berechtigungsrisiken

HackTricks Cloud verwaltet die gemeinsamen Daten zum Schweregrad von Berechtigungen, die von [CloudPEASS](https://github.com/peass-ng/CloudPEASS) und [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) verwendet werden. Bearbeite hier die kanonische Plattformdatei statt der generierten Kopien in einem der beiden Consumer.

- **Kritisch**: Berechtigungen, die direkt oder nahezu unabhängig davon mächtige Privilegien gewähren, eine Identität erzeugen oder privilegierte Ausführung ermöglichen.
- **Hoch**: Zugriff auf sensible Informationen oder Credentials oder ein bedingter Pfad zur Privilege Escalation.
- **Mittel**: DoS/Break, Betriebsstörungen, gewöhnliche Änderungen oder bedingte Fähigkeiten ohne nachgewiesenen Pfad zu sensiblen Daten oder Privilegien.
- **Niedrig**: Gewöhnliche Discovery und Zugriff auf Metadaten.

Es gibt eine kanonische YAML-Datei pro Plattform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) und [Kubernetes](k8s.yaml). Dies sind maschinenlesbare Dateien; die Plattformseiten zeigen ihr vollständiges YAML im Browser an und erklären, wie sie bearbeitet werden. Der Inline-Viewer verwendet die Kopie des Buchs, während die PEASS-Workflows die kanonischen Dateien von GitHub abrufen.

## Cloud-Provider-Dateien

`version` und `provider` identifizieren das Schema. `permission_categories` enthält die vier einzelnen Berechtigungslisten. Verschiebe eine Berechtigung zwischen den Listen, um ihre Einstufung zu ändern. Die Zuordnung von AWS und Azure ignoriert die Groß-/Kleinschreibung; bei GCP wird die Groß-/Kleinschreibung berücksichtigt. Aliase für die Groß-/Kleinschreibung dürfen innerhalb desselben Schweregrads wiederholt werden, widersprüchliche Einstufungen werden jedoch abgelehnt.

`severity_overrides` enthält geprüfte Ausnahmen von allgemeinen Regeln. Wenn eine Ausnahme ebenfalls im Katalog vorkommt, müssen beide Einträge übereinstimmen. `severity_caps` verhindert, dass eine Kombination ausgewählte Berechtigungen höher einstuft. `non_permission_identifiers` schließt dokumentierte API-Methodennamen, Condition Keys und andere Zeichenfolgen aus, die keine tatsächlichen Autorisierungsberechtigungen sind.

`combinations.critical` und `combinations.high` sind Listen von Berechtigungslisten: Jedes Element einer inneren Liste muss gewährt werden, damit diese Kombination gilt. Halte Kombinationen zusammen; würden sie in einzelne Berechtigungen aufgeteilt, würde das Risiko überbewertet. Vorhandene exakte und reguläre Ausdrucksfelder bleiben der Fallback für Berechtigungen, die im Katalog fehlen. Eine vollständige Neufassung des Classifiers oder ein neues Matching-Verhalten erfordert weiterhin Codeänderungen in den Consumern.

## Kubernetes-Datei

`rules` ist geordnet: Die erste passende Regel gewinnt. Jede Regel besitzt eine eindeutige `id`, ein `match`, einen `severity`-Wert und eine Beschreibung in verständlicher Sprache. Füge eine spezifischere Regel vor einer allgemeineren ein oder ändere den Schweregrad einer bestehenden Regel. Bewahre den abschließenden bedingungslosen Fallback.

Matches verwenden `all`, `any` und `not` zur Komposition oder einen Vergleich aus `field`, `op` und `value`. Verfügbare Felder sind `group`, `resource`, `subresource`, `full` (Ressource/Subressource), `verb`, `namespace`, `name`, `path` (kleingeschriebene Non-Resource-URL), `non_resource_url`, `mode` und `delegated_verb`. Mögliche Operationen sind `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` und `truthy` (kein Wert erforderlich). `always: true` passt auf alles. Werte für Group, Resource, Subresource und Verb werden kleingeschrieben. Ein literaler Wildcard wird als `'*'` geschrieben; das Matching eines Wildcard-Grants wird in den Regeln ausdrücklich angegeben und nicht durch eine Shell-Pattern-Erweiterung umgesetzt.

`severity_when` wählt optional einen anderen Schweregrad für eine passende Bedingung aus. `severity: delegated` ist für eingeschränkte Impersonation reserviert: Die Map `delegated_severities` wandelt die Einstufung der delegierten Aktion in die bedingte Einstufung um. Platzhalter in Beschreibungen können auf die verfügbaren Felder verweisen, etwa `{full}` und `{verb}`. Die Regeln sind Daten und werden niemals als Python- oder Shell-Code ausgewertet.

## Validierung und Synchronisierung

Führe vor dem Einreichen von Änderungen mit installiertem PyYAML `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` aus. Der Pull-Request-Workflow des Buchs führt dieselbe Validierung aus.

Jeden Montag checken beide Consumer-Repositories den aktuellen `master` dieses Buchs aus, validieren alle vier Dateien, vergleichen die SHA-256-Hashes und aktualisieren ihre gebündelten YAML-Dateien sowie die generierten Legacy-Listen. Ein Source-Manifest zeichnet die Revision des Buchs und den Hash jeder Datei auf. Nicht zusammenhängende Änderungen am Buch führen zu keinem Consumer-Commit. Jeder Workflow unterstützt außerdem eine manuelle Ausführung. Tests laufen, bevor der Workflow geänderte Daten in den Standard-Branch des Consumers committet; bei Fehlern bleibt dieser Branch unverändert. Die Consumer verwenden zwischen den Aktualisierungen weiterhin ihre gebündelten Kopien offline.

Um einen Consumer lokal zu aktualisieren, führe `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` aus. Füge `--check` hinzu, um veraltete Kopien zu erkennen, ohne sie zu schreiben.

Das Abrufen der Quellen wird in beiden Consumern fünfmal wiederholt, mit begrenzten Checkout-Deadlines und zunehmenden Verzögerungen. Unvollständige Downloads verbleiben in temporären Verzeichnissen; nach ausgeschöpften Wiederholungsversuchen bleiben die vorhandenen gebündelten Daten unverändert.
