# AGENTS.md

Orientación para futuros agentes que trabajen en este repositorio.

## Contexto del repositorio

Este es el repositorio mdBook de HackTricks Cloud. El libro principal relacionado se encuentra en:

`/Users/carlospolop/git/hacktricks`

Los cambios en el comportamiento compartido del tema o de la búsqueda a menudo deben aplicarse en ambos repositorios.

## Contrato de carga del índice de búsqueda

La interfaz de búsqueda personalizada se encuentra en:

`theme/ht_searcher.js`

También puede existir una copia generada en:

`book/theme/ht_searcher.js`

Si production implementa el directorio `book/` ya compilado, actualiza ambas copias o vuelve a compilar el
libro antes del despliegue.

El orden de carga del índice de búsqueda es importante y sensible a los costos:

1. Carga todos los índices de búsqueda específicos de cada idioma y de reserva desde el repositorio de GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Solo si todos los candidatos alojados en GitHub fallan, utiliza como reserva el resultado de mdBook del mismo origen.

No coloques la reserva local `/searchindex.js` antes de ninguna reserva alojada en GitHub, como
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` desde `cloud.hacktricks.wiki` en production es costoso.

Para este repositorio, la reserva local esperada es:

`/searchindex.js`

La reserva del libro principal para este repositorio es:

`/searchindex-book.js`

Ese archivo solo es una reserva. La fuente principal debe seguir siendo los archivos remotos
`searchindex-<lang>.js.gz` y `searchindex-cloud-<lang>.js.gz` en
`HackTricks-wiki/hacktricks-searchindex`.

## Publicación del índice de búsqueda

Los workflows que publican índices de búsqueda comprimidos y cifrados en
`HackTricks-wiki/hacktricks-searchindex` son:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

El archivo fuente generado es `book/searchindex.js`. Los nombres de los artefactos remotos publicados son:

- `searchindex-cloud-v2-en.json.gz` (índice compacto preferido)
- `searchindex-cloud-v2-<lang>.json.gz` (índice compacto preferido)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

El loader del navegador prioriza el artefacto compacto v2 y conserva el artefacto `.js.gz` como
reserva heredada. Ambos son payloads gzip cifrados con XOR mediante la clave definida en `theme/ht_searcher.js`.

## Compilación y validación

Comprobaciones locales habituales:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` falla, comprueba:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edición

- Prefiere `rg` para realizar búsquedas.
- Mantén el resultado generado de `book/` fuera de los commits, salvo que se solicite explícitamente. Las correcciones del loader de búsqueda son una excepción cuando sea necesario corregir inmediatamente las páginas ya compiladas.
- Si cambias el comportamiento compartido del tema, compara y actualiza el archivo correspondiente en
`/Users/carlospolop/git/hacktricks`.
- No reviertas cambios locales no relacionados.
