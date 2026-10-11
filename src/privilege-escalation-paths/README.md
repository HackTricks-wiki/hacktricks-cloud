# Rutas de escalada de privilegios

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud mantiene el catálogo de escalada de privilegios legible por máquinas que consume [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Cada técnica indica qué permisos debe tener efectivamente un principal y en qué recursos para obtener los privilegios de un conjunto de principales objetivo. Blue-CloudPEASS evalúa estas entradas sin conexión, usando una instantánea de inventario de solo lectura, y representa rutas de ataque entre principales, con la política o vinculación que concede los permisos como evidencia y la mitigación que elimina la ruta. Edita los archivos canónicos aquí, no las copias del consumidor.

Las entradas describen solo los requisitos previos, los objetivos alcanzables y la mitigación. No contienen comandos, payloads ni pasos de ejecución; la página de HackTricks enlazada explica la técnica.

## Estructura

Hay un directorio por plataforma (`aws`, `gcp`, `azure`, `k8s`) y un archivo `<service>.yaml` por servicio; cada uno contiene una lista YAML de técnicas. Los archivos llamados `_excluded*.yaml` enumeran técnicas de HackTricks revisadas que intencionalmente no tienen una entrada, como las de post-exploitation, persistence o las que no pueden modelarse a partir de la configuración, junto con el motivo. `privesc-technique.schema.json` es el JSON Schema exportado para completar y validar en el editor.

## Campos de las técnicas

- `id`: identificador único global, en minúsculas y kebab-case, con el prefijo de la plataforma.
- `provider`, `service`, `title` y `summary`: una oración que describe qué obtiene la fuente.
- `source`: la página y el ancla de HackTricks que documentan la técnica, relativas a este libro. `source_revision` es el commit del libro que se consultó.
- `requires`: los permisos que debe tener la fuente. `all_of` enumera todos los elementos requeridos y `any_of`, las alternativas. Los elementos de AWS y GCP usan `action` y `resource`; los de Azure, `action` (o `data_action`) y `scope`; los de Entra ID, `entra_permission` o `entra_role`; y los de Kubernetes, `verb`, `resource`, `subresource`, `api_group` y `namespace`. Los marcadores de posición, como `{target.arn}`, vinculan un requisito al objetivo.
- `target`: el `kind` del objetivo, un `selector` cuyas condiciones deben cumplirse todas para que un principal sea alcanzable y su `scope`.
- `conditions` y `blockers`: lo que puede impedir la ruta en la práctica, como claves de condición, SCPs, límites o políticas de admisión.
- `confidence`, `severity`, `mitigation`, `references` y `notes` opcional.

Los campos, tipos de objetivo, claves de selector y marcadores de posición desconocidos se rechazan en lugar de ignorarse, por lo que una entrada nunca puede ampliar o reducir silenciosamente su conjunto de objetivos. Primero añade compatibilidad con un nuevo selector en el evaluador del consumidor.

## Validación y sincronización

Ejecuta `python scripts/validate_privesc_paths.py --book-root .` con PyYAML instalado antes de enviar los cambios. Comprueba la estructura de directorios, cada entrada mediante el cargador estricto del evaluador (`scripts/privesc_paths_schema.py`, una copia del módulo de esquema de Blue-CloudPEASS), que los ids sean únicos, que exista en este libro cada página `source` y que el JSON Schema esté actualizado. El flujo de trabajo de pull requests del libro ejecuta la misma validación.

Cada lunes, Blue-CloudPEASS obtiene la versión actual de `master` de este libro, valida estos archivos y compara el hash SHA-256 de cada archivo con los hashes registrados durante la sincronización anterior. Las adiciones, actualizaciones y eliminaciones upstream reemplazan las copias sin modificar del consumidor. Si un archivo cambió en ambos lados, se informa como conflicto, y los ids de técnicas nunca se eliminan sin un registro revisado explícitamente. Si el contenido no es válido o falla una prueba, la rama predeterminada del consumidor no cambia. Los cambios no relacionados en el libro no generan ningún commit en el consumidor.
{{#include ../banners/hacktricks-training.md}}
