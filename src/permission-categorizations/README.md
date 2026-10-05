# Categorizaciones de riesgo de permisos

HackTricks Cloud mantiene los datos compartidos de severidad de permisos consumidos por [CloudPEASS](https://github.com/peass-ng/CloudPEASS) y [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edita aquí el archivo canónico de la plataforma, en lugar de las copias generadas en cualquiera de los dos consumidores.

- **Critical**: permisos que conceden directamente, o casi de forma independiente, privilegios potentes, acuñan una identidad o permiten una ejecución privilegiada.
- **High**: acceso a información sensible, credenciales o una ruta condicional de escalada de privilegios.
- **Medium**: DoS/Break, interrupción operativa, cambios ordinarios o capacidades condicionales sin una ruta demostrada hacia datos sensibles o privilegios.
- **Low**: descubrimiento ordinario y acceso a metadatos.

Existe un archivo YAML canónico por plataforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) y [Kubernetes](k8s.yaml). Estos son archivos legibles por máquinas; las páginas de las plataformas explican cómo editarlos.

## Archivos de proveedores cloud

`version` y `provider` identifican el esquema. `permission_categories` contiene las cuatro listas individuales de permisos. Mueve un permiso entre listas para cambiar su clasificación. La coincidencia de AWS y Azure ignora las mayúsculas y minúsculas; la coincidencia de GCP conserva las mayúsculas y minúsculas. Los alias de mayúsculas y minúsculas pueden repetirse dentro de la misma severidad, pero las clasificaciones en conflicto se rechazan.

`severity_overrides` contiene excepciones auditadas a las reglas genéricas. Si una excepción también aparece en el catálogo, ambas entradas deben coincidir. `severity_caps` impide que una combinación eleve la clasificación de determinados permisos. `non_permission_identifiers` excluye nombres de métodos de API documentados, claves de condición y otras cadenas que no son permisos de autorización reales.

`combinations.critical` y `combinations.high` son listas de listas de permisos: todos los elementos de una lista interna deben estar concedidos para que se aplique esa combinación. Mantén las combinaciones juntas; dividirlas en concesiones individuales exageraría el riesgo. Los campos exactos y de expresiones regulares existentes siguen siendo el fallback para los permisos ausentes del catálogo. Una reescritura completa del clasificador o un nuevo comportamiento de coincidencia aún requiere cambios de código en los consumidores.

## Archivo de Kubernetes

`rules` está ordenado: gana la primera regla coincidente. Cada regla tiene un `id` único, un `match`, una `severity` y una `description` en lenguaje sencillo. Añade una regla más específica antes de una más amplia o cambia la severidad de una regla existente. Conserva el fallback final incondicional.

Las coincidencias usan `all`, `any` y `not` para la composición, o una comparación de `field`, `op` y `value`. Los campos disponibles son `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL de recurso no perteneciente a la API en minúsculas), `non_resource_url`, `mode` y `delegated_verb`. Las operaciones son `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` y `truthy` (no requiere valor). `always: true` coincide con todo. Los valores de group, resource, subresource y verb están en minúsculas. Un wildcard literal se escribe como `'*'`; la coincidencia con una concesión wildcard es explícita en las reglas, en lugar de expandirse como un patrón de shell.

`severity_when` selecciona opcionalmente otra severidad para una condición coincidente. `severity: delegated` está reservado para la suplantación restringida: su mapa `delegated_severities` convierte la clasificación de la acción delegada en la clasificación condicional. Los placeholders de la descripción pueden hacer referencia a los campos disponibles, como `{full}` y `{verb}`. Las reglas son datos y nunca se evalúan como código Python o shell.

## Validación y sincronización

Ejecuta `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` con PyYAML instalado antes de enviar los cambios. El workflow de pull request del libro ejecuta la misma validación.

Cada lunes, ambos repositorios consumidores hacen checkout del `master` actual de este libro, validan los cuatro archivos, comparan los hashes SHA-256 y actualizan sus archivos YAML incluidos y sus listas legacy generadas. Un manifiesto de origen registra la revisión del libro y el hash de cada archivo. Los cambios no relacionados en el libro no producen ningún commit en los consumidores. Cada workflow también admite una ejecución manual. Las pruebas se ejecutan antes de que el workflow haga commit de los datos modificados en la rama predeterminada del consumidor; los fallos dejan esa rama sin cambios. Los consumidores continúan usando sus copias incluidas offline entre actualizaciones.

Para actualizar localmente un consumidor, ejecuta `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Añade `--check` para detectar copias obsoletas sin escribir sobre ellas.
