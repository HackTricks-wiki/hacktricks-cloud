# Rutas de escalada de privilegios

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud mantiene el catálogo de escalada de privilegios legible por máquina que consume [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Cada técnica indica qué permisos debe tener efectivamente un principal y sobre qué recursos para obtener los privilegios de un conjunto de principales objetivo. Blue-CloudPEASS evalúa estas entradas sin conexión contra una instantánea de inventario de solo lectura y dibuja rutas de ataque entre principales, con la política o el binding que concede los permisos como evidencia y la mitigación que elimina la ruta. Edita aquí los archivos canónicos, no las copias del consumidor.

Las entradas describen únicamente los prerrequisitos, los objetivos alcanzables y la mitigación. No contienen comandos, payloads ni pasos de ejecución; la página de HackTricks enlazada explica la técnica.

## Estructura

Hay un directorio por plataforma (`aws`, `gcp`, `azure`, `k8s`) y un archivo `<service>.yaml` por servicio, cada uno con una lista YAML de técnicas. Los archivos llamados `_excluded*.yaml` enumeran técnicas de HackTricks revisadas que intencionalmente no tienen una entrada, como las de post-exploitation, persistence o las técnicas que no pueden modelarse a partir de la configuración; también indican el motivo. `privesc-technique.schema.json` es el JSON Schema exportado para autocompletado y validación en el editor.

## Campos de las técnicas

- `id`: identificador globalmente único, en minúsculas y kebab-case, con el prefijo de la plataforma.
- `provider`, `service`, `title` y `summary`: una oración que describe qué obtiene el origen.
- `source`: la página y el anchor de HackTricks que documentan la técnica, con una ruta relativa a este libro. `source_revision` es el commit del libro que se consultó.
- `requires`: los permisos que debe tener el origen. `all_of` enumera todos los elementos necesarios y `any_of` enumera las alternativas. Los elementos de AWS y GCP usan `action` y `resource`; los de Azure usan `action` (o `data_action`) y `scope`; los de Entra ID usan `entra_permission` o `entra_role`; y los de Kubernetes usan `verb`, `resource`, `subresource`, `api_group` y `namespace`. Los placeholders, como `{target.arn}`, vinculan un requisito con el objetivo.
- `target`: el `kind` del objetivo, un `selector` cuyas condiciones deben cumplirse todas para que un principal sea alcanzable, y su `scope`.
- `conditions` y `blockers`: lo que puede impedir la ruta en la práctica, como condition keys, SCPs, boundaries o admission policies.
- `confidence`, `severity`, `mitigation`, `references` y `notes` opcional.

Los campos desconocidos, los tipos de objetivo, las claves de selector y los placeholders se rechazan en lugar de ignorarse, para que una entrada nunca pueda ampliar ni reducir silenciosamente el conjunto de objetivos. Primero, añade compatibilidad con cualquier selector nuevo en el evaluador del consumidor.

### Uniones del schema v2

El loader de v2 añade dos placeholders y un selector de AWS, y permite usar el selector existente de K8s para pods en ejecución en objetivos de GCP. Estos campos requieren una unión exacta con el inventario recopilado; si falta inventario, la cobertura es desconocida, no se considera una ruta alcanzable.

| Campo | Uso y estructura requerida |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` y `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Úsalos juntos en un objetivo AWS `aws_account_admin`. Cada alternativa de requisitos debe incluir `iam:CreatePolicyVersion` sobre ese placeholder. La política debe estar adjunta a un rol que el origen pueda asumir en la misma cuenta; el evaluador comprueba la capacidad de versiones de la política y vuelve a calcular los permisos efectivos del rol. No se cubre `SetDefaultPolicyVersion`. |
| `target.selector.k8s_sa_used_by_running_pod: true` | En un objetivo GCP `k8s_service_account` con `scope: cluster`, selecciona los KSAs usados por pods en ejecución con un token disponible en el clúster GKE coincidente. No lo combines con `k8s_sa_in_cluster` ni con `k8s_sa_has_token_secret`. El uso existente en K8s no cambia. |
| `{source_rolebound_clusterrole}` | Úsalo como `resource_name` en requisitos de K8s `clusterroles` con `api_group: rbac.authorization.k8s.io` y `namespace: "*"`. Cada alternativa necesita `escalate` y `update` o `patch` sobre el mismo nombre. El objetivo debe ser un `k8s_service_account` con `scope: same_namespace` y `selector.k8s_sa_in_namespace: "{target.namespace}"`; un RoleBinding debe vincular al origen en ese namespace. |

## Validación y sincronización

Antes de enviar los cambios, ejecuta `python scripts/validate_privesc_paths.py --book-root .` con PyYAML instalado. Comprueba la estructura de directorios, cada entrada mediante el loader estricto del evaluador (`scripts/privesc_paths_schema.py`, una copia del módulo de schema de Blue-CloudPEASS), los ids únicos, las páginas de origen y sus anchors de encabezado, y que el JSON Schema esté actualizado. Usa `--peaso-root /path/to/Blue-CloudPEASS` para comparar también, byte por byte, ambos archivos de schema con los del consumidor. El workflow de pull request del libro ejecuta la misma validación.

Cada lunes, Blue-CloudPEASS obtiene el `master` actual de este libro, valida estos archivos y compara el hash SHA-256 de cada archivo con los hashes registrados durante la sincronización anterior. Las adiciones, actualizaciones y eliminaciones en el repositorio original reemplazan las copias sin cambios del consumidor. Si un archivo cambia en ambos lados, se informa como conflicto; los ids de las técnicas nunca se eliminan sin un ledger revisado explícitamente. Si el contenido no es válido o falla una prueba, la rama predeterminada del consumidor no cambia. Los cambios no relacionados en el libro no generan ningún commit en el consumidor.
{{#include ../banners/hacktricks-training.md}}
