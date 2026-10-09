# Catégorisations des risques liés aux permissions

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud maintient les données partagées de sévérité des permissions utilisées par [CloudPEASS](https://github.com/peass-ng/CloudPEASS) et [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Modifiez ici le fichier canonique de la plateforme, plutôt que les copies générées dans l'un ou l'autre des consommateurs.

- **Critical** : permissions qui accordent directement, ou presque à elles seules, des privilèges puissants, créent une identité ou permettent une exécution privilégiée.
- **High** : accès à des informations sensibles, à des identifiants ou à une voie conditionnelle d'escalade de privilèges.
- **Medium** : DoS/Break, perturbation opérationnelle, modifications ordinaires ou fonctionnalités conditionnelles sans voie démontrée vers des données sensibles ou des privilèges.
- **Low** : découverte ordinaire et accès aux métadonnées.

Il existe un fichier YAML canonique par plateforme : [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) et [Kubernetes](k8s.yaml). Ces fichiers lisibles par machine sont affichés intégralement dans le navigateur sur les pages des plateformes, qui expliquent également comment les modifier. Le visualiseur intégré utilise la copie du livre, tandis que les workflows PEASS récupèrent les fichiers canoniques depuis GitHub.

## Fichiers des fournisseurs cloud

`version` et `provider` identifient le schéma. `permission_categories` contient les quatre listes de permissions individuelles. Déplacez une permission d'une liste à une autre pour modifier son niveau. La recherche AWS et Azure ignore la casse ; celle de GCP la respecte. Les alias ne différant que par la casse peuvent être répétés au sein d'un même niveau de sévérité, mais les niveaux contradictoires sont rejetés.

`severity_overrides` contient les exceptions aux règles génériques qui ont été auditées. Si une exception figure aussi dans le catalogue, les deux entrées doivent concorder. `severity_caps` empêche une combinaison d'augmenter le niveau de certaines permissions. `non_permission_identifiers` exclut les noms documentés de méthodes d'API, les clés de condition et les autres chaînes qui ne sont pas de véritables permissions d'autorisation.

`combinations.critical` et `combinations.high` sont des listes de listes de permissions : chaque élément d'une liste interne doit être accordé pour que la combinaison s'applique. Gardez les combinaisons groupées ; les diviser en autorisations individuelles exagérerait le risque. Les champs existants de correspondance exacte et d'expressions régulières restent la solution de repli pour les permissions absentes du catalogue. Toute refonte complète du classificateur ou ajout d'un nouveau comportement de correspondance nécessite toujours des modifications du code des consommateurs.

## Fichier Kubernetes

`rules` est ordonné : la première règle correspondante est appliquée. Chaque règle a un `id` unique, un critère `match`, un niveau `severity` et une `description` en langage courant. Ajoutez une règle plus spécifique avant une règle plus générale, ou modifiez le niveau d'une règle existante. Conservez la règle de repli inconditionnelle finale.

Les critères utilisent `all`, `any` et `not` pour la composition, ou une comparaison `field`, `op` et `value`. Les champs disponibles sont `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL non liée aux ressources en minuscules), `non_resource_url`, `mode` et `delegated_verb`. Les opérations sont `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` et `truthy` (aucune valeur requise). `always: true` correspond à tout. Les valeurs de group, resource, subresource et verb sont en minuscules. Un caractère générique littéral s'écrit `'*'` ; les règles indiquent explicitement la correspondance avec une autorisation générique, plutôt que de développer des motifs de shell.

`severity_when` sélectionne facultativement un autre niveau de sévérité en fonction d'une condition correspondante. `severity: delegated` est réservé à l'impersonation contrainte : sa map `delegated_severities` convertit la classification de l'action déléguée en niveau conditionnel. Les espaces réservés de la description peuvent faire référence aux champs disponibles, tels que `{full}` et `{verb}`. Les règles sont des données et ne sont jamais évaluées comme du code Python ou shell.

## Validation et synchronisation

Avant de soumettre des modifications, exécutez `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` avec PyYAML installé. Le workflow de pull request du livre effectue la même validation.

Chaque lundi, les deux dépôts consommateurs récupèrent la version actuelle de `master` de ce livre, valident les quatre fichiers, comparent leurs hachages SHA-256 et mettent à jour leurs fichiers YAML intégrés ainsi que leurs listes historiques générées. Un manifeste source enregistre la révision du livre et le hachage de chaque fichier. Les modifications sans rapport dans le livre ne génèrent aucun commit dans les dépôts consommateurs. Chaque workflow prend également en charge une exécution manuelle. Les tests s'exécutent avant que le workflow ne valide les données modifiées dans la branche par défaut du consommateur ; en cas d'échec, cette branche reste inchangée. Les consommateurs continuent d'utiliser leurs copies intégrées hors ligne entre les mises à jour.

Pour effectuer une mise à jour locale dans un dépôt consommateur, exécutez `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Ajoutez `--check` pour détecter les copies obsolètes sans les modifier.

La récupération des sources par les deux consommateurs fait cinq tentatives, avec des délais d'expiration limités pour le checkout et des intervalles croissants. Les téléchargements incomplets restent dans des répertoires temporaires ; une fois les tentatives épuisées, les données intégrées existantes ne sont pas modifiées.
{{#include ../banners/hacktricks-training.md}}
