# Kategorisierungen von Berechtigungsrisiken

HackTricks Cloud verwaltet die gemeinsamen Schweregraddaten für Berechtigungen, die von [CloudPEASS](https://github.com/peass-ng/CloudPEASS) und [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) verwendet werden. Bearbeite hier die kanonische Plattformdatei statt der generierten Kopien in einem der beiden Consumer.

- **Critical**: Berechtigungen, die direkt oder nahezu unabhängig davon weitreichende Privilegien gewähren, eine Identität erstellen oder privilegierte Ausführung ermöglichen.
- **High**: Zugriff auf vertrauliche Informationen oder Zugangsdaten oder ein bedingter Pfad zur Privilege Escalation.
- **Medium**: DoS/Break, betriebliche Störungen, gewöhnliche Änderungen oder bedingte Fähigkeiten ohne nachgewiesenen Pfad zu vertraulichen Daten oder Privilegien.
- **Low**: Gewöhnliche Discovery und Zugriff auf Metadaten.

Es gibt eine kanonische YAML-Datei pro Plattform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) und [Kubernetes](k8s.yaml). Dies sind maschinenlesbare Dateien; die Plattformseiten erklären, wie sie bearbeitet werden.

## Cloud-Provider-Dateien

`version` und `provider` identifizieren das Schema. `permission_categories` enthält die vier einzelnen Berechtigungslisten. Verschiebe eine Berechtigung zwischen den Listen, um ihre Einstufung zu ändern. Beim Matching von AWS und Azure wird die Groß-/Kleinschreibung ignoriert; beim Matching von GCP wird sie beibehalten. Aliase mit unterschiedlicher Groß-/Kleinschreibung dürfen innerhalb desselben Schweregrads wiederholt werden, widersprüchliche Einstufungen werden jedoch abgelehnt.

`severity_overrides` enthält geprüfte Ausnahmen von allgemeinen Regeln. Wenn eine Ausnahme auch im Katalog vorkommt, müssen beide Einträge übereinstimmen. `severity_caps` verhindert, dass eine Kombination ausgewählte Berechtigungen hochstuft. `non_permission_identifiers` schließt dokumentierte API-Methodennamen, Bedingungsschlüssel und andere Zeichenfolgen aus, die keine tatsächlichen Autorisierungsberechtigungen sind.

`combinations.critical` und `combinations.high` sind Listen von Berechtigungslisten: Jedes Element einer inneren Liste muss gewährt werden, damit diese Kombination greift. Halte Kombinationen zusammen; sie in einzelne Grants aufzuteilen, würde das Risiko überbewerten. Vorhandene Felder für exakte Übereinstimmungen und reguläre Ausdrücke bleiben der Fallback für Berechtigungen, die im Katalog fehlen. Eine vollständige Überarbeitung des Classifiers oder neues Matching-Verhalten erfordert weiterhin Codeänderungen in den Consumern.

## Kubernetes-Datei

`rules` ist geordnet: Die erste passende Regel gewinnt. Jede Regel verfügt über eine eindeutige `id`, ein `match`, einen `severity` und eine Beschreibung in Klartext. Füge eine spezifischere Regel vor einer allgemeineren ein oder ändere den Schweregrad einer bestehenden Regel. Bewahre den abschließenden unbedingten Fallback.

Matches verwenden `all`, `any` und `not` zur Komposition oder einen Vergleich aus `field`, `op` und `value`. Verfügbare Felder sind `group`, `resource`, `subresource`, `full` (Ressource/Subressource), `verb`, `namespace`, `name`, `path` (kleingeschriebene Non-Resource-URL), `non_resource_url`, `mode` und `delegated_verb`. Verfügbare Operationen sind `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` und `truthy` (kein Wert erforderlich). `always: true` passt auf alles. Werte für Group, Resource, Subresource und Verb werden kleingeschrieben. Ein literaler Wildcard wird als `'*'` geschrieben; das Matching eines Wildcard-Grants wird in den Regeln ausdrücklich angegeben und nicht als Shell-Pattern-Expansion behandelt.

`severity_when` wählt optional einen anderen Schweregrad für eine passende Bedingung aus. `severity: delegated` ist für eingeschränkte Impersonation reserviert: Die Map `delegated_severities` wandelt die Klassifizierung der delegierten Aktion in die bedingte Einstufung um. Platzhalter in Beschreibungen können auf die verfügbaren Felder verweisen, etwa `{full}` und `{verb}`. Die Regeln sind Daten und werden niemals als Python- oder Shell-Code ausgewertet.

## Validierung und Synchronisierung

Führe vor dem Einreichen von Änderungen mit installiertem PyYAML `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` aus. Der Pull-Request-Workflow des Buchs führt dieselbe Validierung aus.

Jeden Montag checken beide Consumer-Repositories den aktuellen `master` dieses Buchs aus, validieren alle vier Dateien, vergleichen SHA-256-Hashes und aktualisieren ihre gebündelten YAML-Dateien sowie die generierten Legacy-Listen. Ein Quellmanifest erfasst die Revision des Buchs und den Hash jeder Datei. Nicht verwandte Änderungen am Buch erzeugen keinen Consumer-Commit. Jeder Workflow unterstützt außerdem eine manuelle Ausführung. Tests laufen, bevor der Workflow geänderte Daten in den Standard-Branch des Consumers committet; Fehler lassen diesen Branch unverändert. Zwischen den Aktualisierungen verwenden die Consumer offline weiterhin ihre gebündelten Kopien.

Um lokal in einem Consumer zu aktualisieren, führe `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` aus. Füge `--check` hinzu, um veraltete Kopien zu erkennen, ohne sie zu schreiben.
