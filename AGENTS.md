# AGENTS.md

Guía para futuros agentes que trabajen en este repositorio.

## Contexto del repositorio

Este es el repositorio mdBook de HackTricks Cloud. El libro principal relacionado se encuentra en:

`/Users/carlospolop/git/hacktricks`

Los cambios en el comportamiento compartido del theme/search a menudo deben aplicarse en ambos repositorios.

## Contrato de carga del índice de búsqueda

La UI de búsqueda personalizada se encuentra en:

`theme/ht_searcher.js`

También puede existir una copia generada en:

`book/theme/ht_searcher.js`

Si production está desplegando el directorio `book/` ya compilado, actualiza ambas copias o recompila el
book antes del despliegue.

La política de origen del índice de búsqueda es importante y sensible a los costes:

- En public hosts, carga todos los candidatos específicos de idioma y de fallback únicamente desde
`HackTricks-wiki/hacktricks-searchindex`. Nunca uses como fallback la salida de mdBook del mismo origen;
servir el índice grande desde `cloud.hacktricks.wiki` en production es costoso.
- En localhost, hosts `.local`/`.internal`, loopback, RFC1918, carrier-grade NAT, link-local o direcciones
IPv6 privadas, carga únicamente la salida de mdBook del mismo origen para que los despliegues locales/de
contenedores sigan siendo autocontenidos. Para una página que no esté en inglés, prueba primero la ruta
local con prefijo de idioma (por ejemplo `/es/searchindex.js`) y usa el índice raíz en inglés únicamente
como fallback.

Para este repositorio, el fallback local esperado es:

`/searchindex.js`

El fallback del libro principal para este repositorio es:

`/searchindex-book.js`

Esos archivos locales son fuentes exclusivas de private networks. Los public hosts deben usar únicamente
los archivos remotos `searchindex-<lang>.js.gz` y `searchindex-cloud-<lang>.js.gz` de
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

El browser loader prioriza el artifact compacto v2 y mantiene el artifact `.js.gz` como fallback legacy.
Ambos son payloads gzip cifrados mediante XOR usando la key definida en `theme/ht_searcher.js`.

El loader debe seguir siendo lazy: la navegación normal por las páginas no debe crear el search worker ni
descargar un índice hasta que el visitante abra o use la búsqueda. Las respuestas remotas comprimidas se
persisten en Cache Storage durante 24 horas por origin, para que las páginas posteriores puedan
reutilizarlas. Conserva el stale-cache fallback cuando falla la actualización de una entrada caducada.

## Compilación y validación

Comprobaciones locales habituales:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` falla, comprueba:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edición

- Prioriza `rg` para las búsquedas.
- Mantén la salida generada de `book/` fuera de los commits salvo que se solicite explícitamente. Las
correcciones del search loader son una excepción cuando las páginas ya compiladas deban corregirse de
inmediato.
- Si cambias el comportamiento compartido del theme, compara y actualiza el archivo correspondiente en
`/Users/carlospolop/git/hacktricks`.
- No reviertas cambios locales no relacionados.
