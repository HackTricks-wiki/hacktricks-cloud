# Catégorisations des risques liés aux permissions

HackTricks Cloud gère les données partagées de sévérité des permissions consommées par [CloudPEASS](https://github.com/peass-ng/CloudPEASS) et [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Modifiez ici le fichier canonique de la plateforme, plutôt que les copies générées dans l'un ou l'autre consommateur.

- **Critical** : permissions qui accordent directement, ou presque indépendamment, des privilèges puissants, créent une identité ou permettent une exécution privilégiée.
- **High** : accès à des informations sensibles, à des credentials ou à un chemin conditionnel d'escalade de privilèges.
- **Medium** : DoS/Break, perturbation opérationnelle, modifications ordinaires ou capacités conditionnelles sans chemin démontré vers des données sensibles ou des privilèges.
- **Low** : découverte ordinaire et accès aux métadonnées.

Il existe un fichier YAML canonique par plateforme : [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) et [Kubernetes](k8s.yaml). Il s'agit de fichiers lisibles par les machines ; les pages des plateformes expliquent comment les modifier.

## Fichiers des cloud providers

`version` et `provider` identifient le schéma. `permission_categories` contient les quatre listes individuelles de permissions. Déplacez une permission d'une liste à une autre pour modifier son niveau. La correspondance pour AWS et Azure ignore la casse ; celle de GCP conserve la casse. Les alias de casse peuvent se répéter au sein d'une même sévérité, mais les évaluations contradictoires sont rejetées.

`severity_overrides` contient les exceptions auditées aux règles génériques. Si une exception apparaît également dans le catalogue, les deux entrées doivent être cohérentes. `severity_caps` empêche une combinaison d'augmenter la sévérité de permissions sélectionnées. `non_permission_identifiers` exclut les noms documentés de méthodes API, les clés de condition et autres chaînes qui ne sont pas de véritables permissions d'autorisation.

`combinations.critical` et `combinations.high` sont des listes de listes de permissions : chaque élément d'une liste interne doit être accordé pour que cette combinaison s'applique. Conservez les combinaisons ensemble ; les diviser en grants individuels surestimerait le risque. Les champs exacts et d'expressions régulières existants restent le fallback pour les permissions absentes du catalogue. Une réécriture complète du classifier ou un nouveau comportement de matching nécessite toujours des modifications du code dans les consommateurs.

## Fichier Kubernetes

`rules` est ordonné : la première règle correspondante est prioritaire. Chaque règle possède un `id` unique, un `match`, une `severity` et une `description` en langage naturel. Ajoutez une règle plus spécifique avant une règle plus générale, ou modifiez la sévérité d'une règle existante. Préservez le fallback final inconditionnel.

Les correspondances utilisent `all`, `any` et `not` pour la composition, ou une comparaison `field`, `op` et `value`. Les champs disponibles sont `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL non-resource en minuscules), `non_resource_url`, `mode` et `delegated_verb`. Les opérations sont `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` et `truthy` (aucune valeur requise). `always: true` correspond à tout. Les valeurs de group, resource, subresource et verb sont en minuscules. Un wildcard littéral s'écrit `'*'` ; la correspondance avec un grant wildcard est explicite dans les règles, plutôt qu'une expansion de pattern shell.

`severity_when` sélectionne éventuellement une autre sévérité pour une condition correspondante. `severity: delegated` est réservé à l'impersonation contrainte : sa map `delegated_severities` convertit la classification de l'action déléguée en niveau conditionnel. Les placeholders de description peuvent référencer les champs disponibles, tels que `{full}` et `{verb}`. Les règles sont des données et ne sont jamais évaluées comme du code Python ou shell.

## Validation et synchronisation

Exécutez `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` avec PyYAML installé avant de soumettre vos modifications. Le workflow de pull-request du livre exécute la même validation.

Chaque lundi, les deux dépôts consommateurs récupèrent le `master` actuel de ce livre, valident les quatre fichiers, comparent les hash SHA-256 et mettent à jour leurs fichiers YAML intégrés ainsi que leurs listes legacy générées. Un manifest source enregistre la révision du livre et le hash de chaque fichier. Les modifications sans rapport dans le livre ne produisent aucun commit chez les consommateurs. Chaque workflow prend également en charge une exécution manuelle. Les tests sont exécutés avant que le workflow ne committe les données modifiées sur la branche par défaut du consommateur ; les échecs laissent cette branche inchangée. Entre les mises à jour, les consommateurs continuent d'utiliser leurs copies intégrées hors ligne.

Pour effectuer une mise à jour locale chez un consommateur, exécutez `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Ajoutez `--check` pour détecter les copies obsolètes sans les écrire.
