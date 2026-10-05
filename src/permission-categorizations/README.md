# Categorizaciones de riesgo de permisos

HackTricks Cloud mantiene los datos compartidos de severidad de permisos consumidos por [CloudPEASS](https://github.com/peass-ng/CloudPEASS) y [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edita aquí el archivo canónico de la plataforma, en lugar de las copias generadas en cualquiera de los dos consumidores.

- **Critical**: permisos que otorgan directamente, o casi de forma independiente, privilegios potentes, crean una identidad o permiten la ejecución privilegiada.
- **High**: acceso a información sensible, credenciales o una ruta condicional de escalada de privilegios.
- **Medium**: DoS/Break, interrupción operativa, cambios ordinarios o capacidades condicionales sin una ruta demostrada hacia datos sensibles o privilegios.
- **Low**: descubrimiento ordinario y acceso a metadatos.

Hay un archivo YAML canónico por plataforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) y [Kubernetes](k8s.yaml). Estos son archivos legibles por máquinas; las páginas de las plataformas muestran su YAML completo en el navegador y explican cómo editarlos. El visor integrado usa la copia del libro, mientras que los workflows de PEASS obtienen los archivos canónicos desde GitHub.

## Archivos de proveedores cloud

`version` y `provider` identifican el esquema. `permission_categories` contiene las cuatro listas individuales de permisos. Mueve un permiso entre las listas para cambiar su clasificación. La coincidencia de AWS y Azure ignora mayúsculas y minúsculas; la coincidencia de GCP conserva las mayúsculas y minúsculas. Los alias de mayúsculas y minúsculas pueden repetirse dentro de la misma severidad, pero se rechazan las clasificaciones conflictivas.

`severity_overrides` contiene excepciones auditadas a las reglas genéricas. Si una excepción también aparece en el catálogo, ambas entradas deben coincidir. `severity_caps` evita que una combinación actualice determinados permisos. `non_permission_identifiers` excluye nombres de métodos de API documentados, claves de condición y otras cadenas que no son permisos de autorización reales.

`combinations.critical` y `combinations.high` son listas de listas de permisos: todos los elementos de una lista interna deben estar concedidos para que se aplique esa combinación. Mantén las combinaciones juntas; dividirlas en concesiones individuales exageraría el riesgo. Los campos exactos y de expresiones regulares existentes siguen siendo el fallback para los permisos ausentes del catálogo. Una reescritura completa del clasificador o un nuevo comportamiento de coincidencia todavía requiere cambios de código en los consumidores.

## Archivo de Kubernetes

`rules` está ordenado: gana la primera regla coincidente. Cada regla tiene un `id` único, un `match`, una `severity` y una `description` en lenguaje sencillo. Añade una regla más específica antes de una más general, o cambia la severidad de una regla existente. Conserva el fallback final incondicional.

Las coincidencias usan `all`, `any` y `not` para la composición, o una comparación de `field`, `op` y `value`. Los campos disponibles son `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL de recurso no perteneciente a la API en minúsculas), `non_resource_url`, `mode` y `delegated_verb`. Las operaciones son `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` y `truthy` (no requiere valor). `always: true` coincide con todo. Los valores de group, resource, subresource y verb están en minúsculas. Un wildcard literal se escribe como `'*'`; la coincidencia con una concesión wildcard se especifica explícitamente en las reglas, en lugar de usar la expansión de patrones del shell.

`severity_when` selecciona opcionalmente otra severidad para una condición coincidente. `severity: delegated` está reservado para la suplantación restringida: su mapa `delegated_severities` convierte la clasificación de la acción delegada en la clasificación condicional. Los placeholders de description pueden hacer referencia a los campos disponibles, como `{full}` y `{verb}`. Las reglas son datos y nunca se evalúan como código Python o shell.

## Validación y sincronización

Ejecuta `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` con PyYAML instalado antes de enviar los cambios. El workflow de pull request del libro ejecuta la misma validación.

Cada lunes, ambos repositorios consumidores hacen checkout del `master` actual de este libro, validan los cuatro archivos, comparan los hashes SHA-256 y actualizan sus archivos YAML incluidos y las listas legacy generadas. Un manifiesto de origen registra la revisión del libro y el hash de cada archivo. Los cambios no relacionados en el libro no producen ningún commit en los consumidores. Cada workflow también admite una ejecución manual. Las pruebas se ejecutan antes de que el workflow haga commit de los datos modificados en la rama predeterminada del consumidor; los fallos dejan esa rama sin cambios. Los consumidores siguen usando sus copias incluidas sin conexión entre actualizaciones.

Para actualizar localmente un consumidor, ejecuta `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Añade `--check` para detectar copias obsoletas sin modificarlas.

La obtención de código fuente en ambos consumidores reintenta cinco veces, con límites de tiempo acotados para el checkout y retrasos crecientes. Las descargas incompletas permanecen en directorios temporales; si se agotan los reintentos, los datos incluidos existentes no se modifican.
