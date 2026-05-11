# AGENTS.md

Guía para futuros agentes que trabajen en este repositorio.

## Contexto del repositorio

Este es el repositorio mdBook de HackTricks Cloud. El libro principal relacionado vive en:

`/Users/carlospolop/git/hacktricks`

Los cambios en el comportamiento compartido del tema/búsqueda a menudo necesitan aplicarse en ambos repositorios.

## Contrato de carga del índice de búsqueda

La interfaz de búsqueda personalizada vive en:

`theme/ht_searcher.js`

También puede haber una copia generada en:

`book/theme/ht_searcher.js`

Si producción está desplegando el directorio ya compilado `book/`, actualiza ambas copias o recompila el
libro antes del despliegue.

El orden de carga del índice de búsqueda es importante y sensible al coste:

1. Carga cada índice de búsqueda específico del idioma y de fallback desde el repositorio de GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Solo si todos los candidatos alojados en GitHub fallan, recurre al mdBook del mismo origen.

No coloques el fallback local `/searchindex.js` antes de ningún fallback alojado en GitHub, como
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` desde `cloud.hacktricks.wiki` en producción es costoso.

Para este repositorio, el fallback local esperado es:

`/searchindex.js`

El fallback del libro principal para este repositorio es:

`/searchindex-book.js`

Ese archivo es solo un fallback. La fuente principal debe seguir siendo los archivos remotos
`searchindex-<lang>.js.gz` y `searchindex-cloud-<lang>.js.gz` en
`HackTricks-wiki/hacktricks-searchindex`.

## Publicación del índice de búsqueda

Los workflows que publican índices de búsqueda comprimidos y cifrados en
`HackTricks-wiki/hacktricks-searchindex` son:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

El archivo fuente generado es `book/searchindex.js`. Los nombres de los artefactos remotos publicados son:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

El cargador del navegador espera que los archivos remotos `.js.gz` sean cargas gzip cifradas con XOR usando la
clave definida en `theme/ht_searcher.js`.

## Compilación y validación

Comprobaciones locales comunes:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` falla, revisa:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edición

- Prefiere `rg` para buscar.
- Mantén la salida generada `book/` fuera de los commits salvo que se solicite explícitamente. Las correcciones del cargador de búsqueda son
una excepción cuando las páginas ya compiladas deben corregirse inmediatamente.
- Si cambias el comportamiento compartido del tema, compara y actualiza el archivo correspondiente en
`/Users/carlospolop/git/hacktricks`.
- No reviertas cambios locales no relacionados.
