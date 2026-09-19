# AGENTS.md

Hinweise für zukünftige Agents, die an diesem Repository arbeiten.

## Repository-Kontext

Dies ist das HackTricks Cloud mdBook-Repository. Das zugehörige Hauptbuch befindet sich unter:

`/Users/carlospolop/git/hacktricks`

Änderungen am gemeinsamen Theme-/Suchverhalten müssen häufig in beiden Repositories angewendet werden.

## Vertrag zum Laden des Suchindex

Die benutzerdefinierte Suchoberfläche befindet sich in:

`theme/ht_searcher.js`

Es kann außerdem eine generierte Kopie unter folgendem Pfad geben:

`book/theme/ht_searcher.js`

Wenn die Produktion das bereits erstellte Verzeichnis `book/` bereitstellt, müssen beide Kopien aktualisiert oder das
Buch vor der Bereitstellung neu erstellt werden.

Die Richtlinie für die Quelle des Suchindex ist wichtig und kostenabhängig:

- Auf öffentlichen Hosts jeden sprachspezifischen und jeden Fallback-Kandidaten ausschließlich von
`HackTricks-wiki/hacktricks-searchindex` laden. Niemals auf die mdBook-Ausgabe derselben Origin zurückgreifen;
das Bereitstellen des großen Index von `cloud.hacktricks.wiki` in der Produktion ist teuer.
- Auf localhost, `.local`-/`.internal`-Hosts, Loopback-, RFC1918-, Carrier-Grade-NAT-, Link-Local- oder
privaten IPv6-Adressen ausschließlich die mdBook-Ausgabe derselben Origin laden, damit lokale/Container-Bereitstellungen
eigenständig bleiben.

Für dieses Repository lautet der erwartete lokale Fallback:

`/searchindex.js`

Der Fallback des Hauptbuchs für dieses Repository lautet:

`/searchindex-book.js`

Diese lokalen Dateien sind ausschließlich Quellen für private Netzwerke. Öffentliche Hosts müssen ausschließlich die
entfernten Dateien `searchindex-<lang>.js.gz` und `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex` verwenden.

## Veröffentlichung des Suchindex

Die Workflows, die verschlüsselte komprimierte Suchindizes in
`HackTricks-wiki/hacktricks-searchindex` veröffentlichen, sind:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die generierte Quelldatei ist `book/searchindex.js`. Die Namen der veröffentlichten entfernten Artefakte sind:

- `searchindex-cloud-v2-en.json.gz` (bevorzugter kompakter Index)
- `searchindex-cloud-v2-<lang>.json.gz` (bevorzugter kompakter Index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Der Browser-Loader bevorzugt das kompakte v2-Artefakt und verwendet das `.js.gz`-Artefakt weiterhin als
Legacy-Fallback. Beide sind XOR-verschlüsselte gzip-Nutzdaten und verwenden den in `theme/ht_searcher.js`
definierten Schlüssel.

Der Loader muss lazy bleiben: Eine normale Seitennavigation darf weder den Search Worker erstellen noch einen Index
herunterladen, bevor der Besucher die Suche öffnet oder verwendet. Entfernte komprimierte Antworten werden pro Origin
24 Stunden lang im Cache Storage gespeichert, damit nachfolgende Seiten sie wiederverwenden können. Beim Aktualisieren
eines abgelaufenen Eintrags muss der Fallback auf den veralteten Cache erhalten bleiben, falls die Aktualisierung
fehlschlägt.

## Build und Validierung

Übliche lokale Prüfungen:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Falls `mdbook build` fehlschlägt, prüfe:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Hinweise zur Bearbeitung

- Für die Suche bevorzugt `rg` verwenden.
- Generierte `book/`-Ausgaben nicht in Commits aufnehmen, sofern dies nicht ausdrücklich angefordert wurde. Änderungen am
  Search Loader sind eine Ausnahme, wenn die bereits erstellten Seiten sofort korrigiert werden müssen.
- Wenn das gemeinsame Theme-Verhalten geändert wird, die entsprechende Datei in
`/Users/carlospolop/git/hacktricks` vergleichen und aktualisieren.
- Keine nicht zusammenhängenden lokalen Änderungen zurücksetzen.
