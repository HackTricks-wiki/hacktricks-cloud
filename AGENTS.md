# AGENTS.md

Anleitung für zukünftige Agents, die an diesem Repository arbeiten.

## Repository-Kontext

Dies ist das HackTricks Cloud mdBook-Repository. Das zugehörige Hauptbuch befindet sich unter:

`/Users/carlospolop/git/hacktricks`

Änderungen am gemeinsamen Theme-/Search-Verhalten müssen häufig in beiden Repositories vorgenommen werden.

## Vertrag zum Laden des Search-Index

Die benutzerdefinierte Search-Oberfläche befindet sich in:

`theme/ht_searcher.js`

Möglicherweise gibt es auch eine generierte Kopie unter:

`book/theme/ht_searcher.js`

Wenn die Produktion das bereits erstellte Verzeichnis `book/` ausliefert, aktualisiere beide Kopien oder erstelle das
Buch vor dem Deployment neu.

Die Richtlinie für die Quelle des Search-Index ist wichtig und kostenrelevant:

- Lade auf öffentlichen Hosts jeden sprachspezifischen und jeden Fallback-Kandidaten ausschließlich aus
`HackTricks-wiki/hacktricks-searchindex`. Führe niemals einen Fallback auf die mdBook-Ausgabe derselben Origin durch;
das Ausliefern des großen Index von `cloud.hacktricks.wiki` in der Produktion ist teuer.
- Lade auf Localhost-, `.local`-/`.internal`-Hosts, Loopback-, RFC1918-, Carrier-Grade-NAT-, Link-Local- oder
privaten IPv6-Adressen ausschließlich die mdBook-Ausgabe derselben Origin, damit lokale/Container-Deployments
eigenständig bleiben. Bei einer nicht-englischen Seite soll zuerst der lokale sprachpräfixierte Pfad versucht werden
(zum Beispiel `/es/searchindex.js`) und der englische Root-Index nur als Fallback verwendet werden.

Für dieses Repo ist der erwartete lokale Fallback:

`/searchindex.js`

Der Fallback des Hauptbuchs für dieses Repo ist:

`/searchindex-book.js`

Diese lokalen Dateien sind ausschließlich Quellen für private Netzwerke. Öffentliche Hosts müssen ausschließlich die
entfernten Dateien `searchindex-<lang>.js.gz` und `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex` verwenden.

## Veröffentlichung des Search-Index

Die Workflows, die verschlüsselte komprimierte Search-Indexe in
`HackTricks-wiki/hacktricks-searchindex` veröffentlichen, sind:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die generierte Quelldatei ist `book/searchindex.js`. Die Namen der veröffentlichten entfernten Artefakte sind:

- `searchindex-cloud-v2-en.json.gz` (bevorzugter kompakter Index)
- `searchindex-cloud-v2-<lang>.json.gz` (bevorzugter kompakter Index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Der Browser-Loader bevorzugt das kompakte v2-Artefakt und behält das `.js.gz`-Artefakt als Legacy-Fallback bei.
Beide sind XOR-verschlüsselte gzip-Payloads und verwenden den in `theme/ht_searcher.js` definierten Schlüssel.

Der Loader muss lazy bleiben: Die normale Seitennavigation darf weder den Search-Worker erstellen noch einen Index
herunterladen, bevor der Besucher die Suche öffnet oder verwendet. Entfernte komprimierte Antworten werden pro Origin
24 Stunden lang im Cache Storage gespeichert, damit nachfolgende Seiten sie wiederverwenden können. Behalte den
Fallback auf veraltete Cache-Einträge bei, wenn die Aktualisierung eines abgelaufenen Eintrags fehlschlägt.

## Build und Validierung

Übliche lokale Prüfungen:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Wenn `mdbook build` fehlschlägt, prüfe:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Hinweise zur Bearbeitung

- Verwende zum Suchen bevorzugt `rg`.
- Halte generierte `book/`-Ausgaben aus Commits heraus, sofern dies nicht ausdrücklich angefordert wurde. Änderungen am
Search-Loader bilden eine Ausnahme, wenn die bereits erstellten Seiten sofort korrigiert werden müssen.
- Wenn du das gemeinsame Theme-Verhalten änderst, vergleiche die entsprechende Datei in
`/Users/carlospolop/git/hacktricks` und aktualisiere sie ebenfalls.
- Verwirf keine nicht verwandten lokalen Änderungen.
