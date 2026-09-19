# AGENTS.md

Hinweise für zukünftige Agents, die an diesem Repository arbeiten.

## Repository-Kontext

Dies ist das HackTricks Cloud mdBook-Repository. Das zugehörige Hauptbuch befindet sich unter:

`/Users/carlospolop/git/hacktricks`

Änderungen am gemeinsamen Theme-/Search-Verhalten müssen häufig in beiden Repositories angewendet werden.

## Vertrag zum Laden des Search-Index

Die benutzerdefinierte Search-UI befindet sich in:

`theme/ht_searcher.js`

Möglicherweise gibt es auch eine generierte Kopie unter:

`book/theme/ht_searcher.js`

Wenn die Produktion das bereits erstellte `book/`-Verzeichnis deployt, aktualisiere beide Kopien oder erstelle das
Book vor dem Deployment neu.

Die Reihenfolge beim Laden des Search-Index ist wichtig und kostenrelevant:

1. Lade jeden sprachspezifischen und Fallback-Search-Index aus dem GitHub-Repository:
`HackTricks-wiki/hacktricks-searchindex`
2. Nur wenn alle auf GitHub gehosteten Kandidaten fehlschlagen, verwende das gleichursprüngliche mdBook-Output als Fallback.

Platziere den lokalen `/searchindex.js`-Fallback nicht vor einem auf GitHub gehosteten Fallback wie
`searchindex-cloud-en.js.gz`. Das Ausliefern von `searchindex.js` von `cloud.hacktricks.wiki` ist in der Produktion teuer.

Für dieses Repository lautet der erwartete lokale Fallback:

`/searchindex.js`

Der Fallback des Hauptbuchs für dieses Repository lautet:

`/searchindex-book.js`

Diese Datei ist nur ein Fallback. Die primäre Quelle muss weiterhin aus den Remote-Dateien
`searchindex-<lang>.js.gz` und `searchindex-cloud-<lang>.js.gz` in
`HackTricks-wiki/hacktricks-searchindex` bestehen.

## Veröffentlichung des Search-Index

Die Workflows, die verschlüsselte komprimierte Search-Index-Dateien in
`HackTricks-wiki/hacktricks-searchindex` veröffentlichen, sind:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Die generierte Quelldatei ist `book/searchindex.js`. Die Namen der veröffentlichten Remote-Artefakte sind:

- `searchindex-cloud-v2-en.json.gz` (bevorzugter kompakter Index)
- `searchindex-cloud-v2-<lang>.json.gz` (bevorzugter kompakter Index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Der Browser-Loader bevorzugt das kompakte v2-Artefakt und behält das `.js.gz`-Artefakt als Legacy-Fallback bei.
Beide sind XOR-verschlüsselte gzip-Payloads und verwenden den in `theme/ht_searcher.js` definierten Schlüssel.

## Build und Validierung

Übliche lokale Prüfungen:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Wenn `mdbook build` fehlschlägt, prüfe:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Hinweise zur Bearbeitung

- Bevorzuge `rg` für die Suche.
- Halte generiertes `book/`-Output aus Commits heraus, sofern dies nicht ausdrücklich angefordert wurde. Änderungen am Search-Loader sind eine
  Ausnahme, wenn die bereits erstellten Seiten sofort korrigiert werden müssen.
- Wenn du das gemeinsame Theme-Verhalten änderst, vergleiche die entsprechende Datei in
`/Users/carlospolop/git/hacktricks` und aktualisiere sie ebenfalls.
- Mache keine unabhängigen lokalen Änderungen rückgängig.
