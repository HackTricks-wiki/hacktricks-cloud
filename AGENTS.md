# AGENTS.md

Hinweise für zukünftige Agents, die in diesem Repository arbeiten.

## Repository-Kontext

Dies ist das HackTricks Cloud mdBook-Repository. Das zugehörige Hauptbuch liegt unter:

`/Users/carlospolop/git/hacktricks`

Änderungen an gemeinsamem Theme-/Search-Verhalten müssen oft in beiden Repositories angewendet werden.

## Search-Index-Loading-Contract

Die benutzerdefinierte Search-UI befindet sich in:

`theme/ht_searcher.js`

Es kann auch eine generierte Kopie unter:

`book/theme/ht_searcher.js`

geben.

Wenn Production das bereits gebaute `book/`-Verzeichnis ausliefert, beide Kopien aktualisieren oder das Buch vor dem Deployment neu bauen.

Die Lade-Reihenfolge des Search-Index ist wichtig und kostenkritisch:

1. Lade jeden sprachspezifischen und Fallback-Search-Index aus dem GitHub-Repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Nur wenn alle GitHub-gehosteten Kandidaten fehlschlagen, auf das same-origin mdBook-Output zurückfallen.

Platziere den lokalen `/searchindex.js`-Fallback nicht vor irgendeinem GitHub-gehosteten Fallback wie
`searchindex-cloud-en.js.gz`. Das Ausliefern von `searchindex.js` von `cloud.hacktricks.wiki` in Production ist teuer.

Für dieses Repo ist der erwartete lokale Fallback:

`/searchindex.js`

Der Main-Book-Fallback für dieses Repo ist:

`/searchindex-book.js`

Diese Datei ist nur ein Fallback. Die primäre Quelle muss weiterhin die entfernten
`searchindex-<lang>.js.gz`- und `searchindex-cloud-<lang>.js.gz`-Dateien in
`HackTricks-wiki/hacktricks-searchindex` bleiben.

## Search-Index-Veröffentlichung

Die Workflows, die verschlüsselte komprimierte Search-Indexes nach
`HackTricks-wiki/hacktricks-searchindex` veröffentlichen, sind:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die generierte Quelldatei ist `book/searchindex.js`. Die veröffentlichten Remote-Artefakt-Namen sind:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Der Browser-Loader erwartet, dass die Remote-`.js.gz`-Dateien XOR-verschlüsselte gzip-Payloads sind, die den
Schlüssel verwenden, der in `theme/ht_searcher.js` definiert ist.

## Build und Validierung

Gängige lokale Prüfungen:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Wenn `mdbook build` fehlschlägt, prüfe:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Bearbeitungshinweise

- Für die Suche bevorzugt `rg` verwenden.
- Generiertes `book/`-Output aus Commits heraushalten, außer es wird ausdrücklich angefordert. Search-Loader-Fixes sind
  eine Ausnahme, wenn die bereits gebauten Seiten sofort korrigiert werden müssen.
- Wenn gemeinsames Theme-Verhalten geändert wird, die passende Datei in
  `/Users/carlospolop/git/hacktricks` vergleichen und aktualisieren.
- Keine unrelated local changes zurücksetzen.
