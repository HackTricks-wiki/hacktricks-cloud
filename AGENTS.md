# AGENTS.md

Guidance for futuros agentes que trabajen en este repositorio.

## Contexto del repositorio

Este es el repositorio mdBook de HackTricks Cloud. El libro principal relacionado se encuentra en:

`/Users/carlospolop/git/hacktricks`

Los cambios en el comportamiento compartido del theme/search a menudo deben aplicarse en ambos repositorios.

## Contrato de carga del índice de búsqueda

La interfaz de búsqueda personalizada se encuentra en:

`theme/ht_searcher.js`

También puede existir una copia generada en:

`book/theme/ht_searcher.js`

Si production está desplegando el directorio `book/` ya compilado, actualiza ambas copias o recompila el
book antes del despliegue.

El orden de carga del índice de búsqueda es importante y sensible a los costes:

1. Carga todos los índices de búsqueda específicos de cada idioma y de fallback desde el repositorio de GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Solo si fallan todos los candidatos alojados en GitHub, utiliza como fallback el output de mdBook del mismo origen.

No coloques el fallback local `/searchindex.js` antes de ningún fallback alojado en GitHub, como
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` desde `cloud.hacktricks.wiki` en production es caro.

Para este repositorio, el fallback local esperado es:

`/searchindex.js`

El fallback del libro principal para este repositorio es:

`/searchindex-book.js`

Ese archivo solo es un fallback. La fuente principal debe seguir siendo los archivos remotos
`searchindex-<lang>.js.gz` y `searchindex-cloud-<lang>.js.gz` en
`HackTricks-wiki/hacktricks-searchindex`.

## Publicación del índice de búsqueda

Los workflows que publican índices de búsqueda comprimidos y cifrados en
`HackTricks-wiki/hacktricks-searchindex` son:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

El archivo fuente generado es `book/searchindex.js`. Los nombres de los artifacts remotos publicados son:

- `searchindex-cloud-v2-en.json.gz` (índice compacto preferido)
- `searchindex-cloud-v2-<lang>.json.gz` (índice compacto preferido)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

El loader del navegador prioriza el artifact compacto v2 y conserva el artifact `.js.gz` como
fallback legacy. Ambos son payloads gzip cifrados mediante XOR usando la clave definida en `theme/ht_searcher.js`.

El loader debe seguir siendo lazy: la navegación normal por las páginas no debe crear el search worker ni descargar un
índice hasta que el visitante abra o utilice la búsqueda. Las respuestas remotas comprimidas se guardan en Cache
Storage durante 24 horas por origin para que las páginas posteriores puedan reutilizarlas. Conserva el
fallback de la caché obsoleta cuando falla la actualización de una entrada expirada.

## Compilación y validación

Comprobaciones locales habituales:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` falla, comprueba:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edición

- Prefiere `rg` para realizar búsquedas.
- Mantén el output generado de `book/` fuera de los commits, salvo que se solicite explícitamente. Las correcciones del search loader son
una excepción cuando sea necesario corregir inmediatamente las páginas ya compiladas.
- Si cambias el comportamiento compartido del theme, compara y actualiza el archivo correspondiente en
`/Users/carlospolop/git/hacktricks`.
- No reviertas cambios locales no relacionados.
