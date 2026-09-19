# AGENTS.md

Directrices para futuros agentes que trabajen en este repositorio.

## Contexto del repositorio

Este es el repositorio mdBook de HackTricks Cloud. El libro principal relacionado se encuentra en:

`/Users/carlospolop/git/hacktricks`

Los cambios en el comportamiento compartido del tema o de la búsqueda suelen tener que aplicarse en ambos repositorios.

## Contrato de carga del índice de búsqueda

La interfaz de búsqueda personalizada se encuentra en:

`theme/ht_searcher.js`

También puede existir una copia generada en:

`book/theme/ht_searcher.js`

Si production está despleciendo el directorio `book/` ya compilado, actualiza ambas copias o vuelve a compilar el libro antes del despliegue.

La política de origen del índice de búsqueda es importante y sensible a los costes:

- En public hosts, carga cada candidato específico del idioma y de fallback únicamente desde `HackTricks-wiki/hacktricks-searchindex`. Nunca uses como fallback la salida de mdBook del mismo origen; servir el índice grande desde `cloud.hacktricks.wiki` en production es caro.
- En localhost, hosts `.local`/`.internal`, loopback, RFC1918, NAT de nivel de operador, direcciones link-local o direcciones IPv6 privadas, carga únicamente la salida de mdBook del mismo origen para que los despliegues locales/de contenedor sigan siendo autosuficientes.

Para este repositorio, el fallback local esperado es:

`/searchindex.js`

El fallback del libro principal para este repositorio es:

`/searchindex-book.js`

Esos archivos locales son únicamente fuentes para redes privadas. Los public hosts deben usar exclusivamente los archivos remotos `searchindex-<lang>.js.gz` y `searchindex-cloud-<lang>.js.gz` de `HackTricks-wiki/hacktricks-searchindex`.

## Publicación del índice de búsqueda

Los workflows que publican índices de búsqueda comprimidos y cifrados en `HackTricks-wiki/hacktricks-searchindex` son:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

El archivo fuente generado es `book/searchindex.js`. Los nombres de los artefactos remotos publicados son:

- `searchindex-cloud-v2-en.json.gz` (índice compacto preferido)
- `searchindex-cloud-v2-<lang>.json.gz` (índice compacto preferido)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

El loader del navegador prioriza el artefacto compacto v2 y conserva el artefacto `.js.gz` como fallback heredado. Ambos son payloads gzip cifrados mediante XOR usando la clave definida en `theme/ht_searcher.js`.

El loader debe seguir siendo lazy: la navegación normal por las páginas no debe crear el search worker ni descargar un índice hasta que el visitante abra o use la búsqueda. Las respuestas remotas comprimidas se conservan en Cache Storage durante 24 horas por origen para que las páginas posteriores puedan reutilizarlas. Conserva el fallback de la caché obsoleta cuando falla la actualización de una entrada caducada.

## Compilación y validación

Comprobaciones locales habituales:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` falla, comprueba:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edición

- Prefiere `rg` para buscar.
- Mantén la salida generada de `book/` fuera de los commits, salvo que se solicite explícitamente. Las correcciones del search loader son una excepción cuando sea necesario corregir inmediatamente las páginas ya compiladas.
- Si cambias el comportamiento compartido del tema, compara y actualiza el archivo correspondiente en
`/Users/carlospolop/git/hacktricks`.
- No reviertas cambios locales no relacionados.
