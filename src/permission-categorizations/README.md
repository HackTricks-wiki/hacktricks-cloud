# Categorizaciones de riesgo de permisos

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud mantiene los datos compartidos de gravedad de permisos que consumen [CloudPEASS](https://github.com/peass-ng/CloudPEASS) y [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edita aquí el archivo canónico de la plataforma, en lugar de las copias generadas en cualquiera de los dos consumidores.

- **Critical**: permisos que otorgan directamente, o casi de forma independiente, privilegios potentes, crean una identidad o permiten la ejecución privilegiada.
- **High**: acceso a información sensible, credenciales o una vía condicional de escalada de privilegios.
- **Medium**: DoS/Break, interrupción operativa, cambios habituales o capacidades condicionales sin una vía demostrada hacia datos sensibles o privilegios.
- **Low**: descubrimiento habitual y acceso a metadatos.

Hay un archivo YAML canónico por plataforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) y [Kubernetes](k8s.yaml). Estos son archivos legibles por máquina; las páginas de las plataformas muestran su YAML completo en el navegador y explican cómo editarlos. El visor integrado utiliza la copia del libro, mientras que los flujos de trabajo de PEASS obtienen los archivos canónicos de GitHub.

## Archivos de proveedores de cloud

`version` y `provider` identifican el esquema. `permission_categories` contiene las cuatro listas individuales de permisos. Mueve un permiso entre listas para cambiar su clasificación. La comparación de AWS y Azure no distingue entre mayúsculas y minúsculas; la de GCP sí. Los alias que solo difieren en mayúsculas y minúsculas pueden repetirse dentro de la misma gravedad, pero se rechazan las clasificaciones en conflicto.

`severity_overrides` contiene excepciones auditadas a las reglas genéricas. Si una excepción también aparece en el catálogo, ambas entradas deben coincidir. `severity_caps` impide que una combinación eleve la clasificación de los permisos seleccionados. `non_permission_identifiers` excluye nombres documentados de métodos de API, claves de condición y otras cadenas que no son permisos de autorización reales.

`combinations.critical` y `combinations.high` son listas de listas de permisos: todos los elementos de una lista interna deben estar concedidos para que se aplique esa combinación. Mantén las combinaciones juntas; dividirlas en permisos individuales exageraría el riesgo. Los campos existentes de coincidencia exacta y expresiones regulares siguen siendo la alternativa para los permisos ausentes del catálogo. Una reescritura completa del clasificador o un nuevo comportamiento de coincidencia aún requieren cambios de código en los consumidores.

## Archivo de Kubernetes

`rules` está ordenado: gana la primera regla coincidente. Cada regla tiene un `id` único, un `match`, una `severity` y una `description` en lenguaje sencillo. Añade una regla más específica antes de una más amplia o cambia la gravedad de una regla existente. Conserva la regla final de reserva incondicional.

Las coincidencias usan `all`, `any` y `not` para la composición, o una comparación de `field`, `op` y `value`. Los campos disponibles son `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL de recurso no convencional en minúsculas), `non_resource_url`, `mode` y `delegated_verb`. Las operaciones son `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` y `truthy` (no requiere valor). `always: true` coincide con todo. Los valores de group, resource, subresource y verb se escriben en minúsculas. Un comodín literal se escribe como `'*'`; las reglas especifican explícitamente la coincidencia con una concesión de comodín, en lugar de expandir patrones de shell.

`severity_when` selecciona opcionalmente otra gravedad para una condición coincidente. `severity: delegated` está reservado para la suplantación restringida: su mapa `delegated_severities` convierte la clasificación de la acción delegada en la clasificación condicional. Los marcadores de posición de la descripción pueden hacer referencia a los campos disponibles, como `{full}` y `{verb}`. Las reglas son datos y nunca se evalúan como código Python o de shell.

## Validación y sincronización

Ejecuta `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` con PyYAML instalado antes de enviar cambios. El flujo de trabajo de pull requests del libro ejecuta la misma validación.

Cada lunes, ambos repositorios consumidores obtienen la versión actual de `master` de este libro, validan los cuatro archivos, comparan los hashes SHA-256 y actualizan sus archivos YAML incluidos y sus listas heredadas generadas. Un manifiesto de origen registra la revisión del libro y el hash de cada archivo. Los cambios no relacionados en el libro no generan commits en los consumidores. Cada flujo de trabajo también admite una ejecución manual. Las pruebas se ejecutan antes de que el flujo de trabajo confirme los datos modificados en la rama predeterminada del consumidor; si fallan, esa rama no cambia. Los consumidores siguen usando sus copias incluidas sin conexión entre actualizaciones.

Para actualizar localmente en un consumidor, ejecuta `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Añade `--check` para detectar copias desactualizadas sin escribir en ellas.

La obtención de fuentes en ambos consumidores reintenta cinco veces, con plazos de checkout limitados y retrasos crecientes. Las descargas incompletas permanecen en directorios temporales; si se agotan los reintentos, los datos incluidos existentes no se modifican.
{{#include ../banners/hacktricks-training.md}}
