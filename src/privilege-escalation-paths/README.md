# Chemins d’escalade de privilèges

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud gère le catalogue des chemins d’escalade de privilèges lisible par machine utilisé par [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Chaque technique indique les permissions qu’un principal doit effectivement détenir, et sur quelles ressources, pour obtenir les privilèges d’un ensemble de principaux cibles. Blue-CloudPEASS évalue ces entrées hors ligne à partir d’un instantané d’inventaire en lecture seule et trace les chemins d’attaque entre principaux, en indiquant comme preuve la policy ou le binding qui accorde les permissions, ainsi que la mesure d’atténuation qui supprime le chemin. Modifiez les fichiers canoniques ici, et non leurs copies chez le consommateur.

Les entrées décrivent uniquement les préconditions, les cibles accessibles et la mesure d’atténuation. Elles ne contiennent aucune commande, payload ou étape d’exécution ; la page HackTricks liée explique la technique.

## Structure

Il existe un répertoire par plateforme (`aws`, `gcp`, `azure`, `k8s`) et un fichier `<service>.yaml` par service, chacun contenant une liste YAML de techniques. Les fichiers nommés `_excluded*.yaml` répertorient les techniques HackTricks examinées qui n’ont volontairement aucune entrée, comme le post-exploitation, la persistence ou les techniques qui ne peuvent pas être modélisées à partir de la configuration ; la raison est précisée. `privesc-technique.schema.json` est le schéma JSON exporté, utilisé pour la complétion et la validation dans l’éditeur.

## Champs des techniques

- `id` : identifiant unique à l’échelle globale, en minuscules et au format kebab-case, préfixé par la plateforme.
- `provider`, `service`, `title` et `summary` : une phrase décrivant ce que la source obtient.
- `source` : la page HackTricks et son ancre documentant la technique, relativement à ce livre. `source_revision` est le commit du livre consulté.
- `requires` : les permissions que la source doit détenir. `all_of` répertorie tous les éléments requis et `any_of` les alternatives. Les éléments AWS et GCP utilisent `action` et `resource`, les éléments Azure utilisent `action` (ou `data_action`) et `scope`, les éléments Entra ID utilisent `entra_permission` ou `entra_role`, et les éléments Kubernetes utilisent `verb`, `resource`, `subresource`, `api_group` et `namespace`. Les espaces réservés comme `{target.arn}` associent une exigence à la cible.
- `target` : le `kind` de la cible, un `selector` dont toutes les conditions doivent être remplies pour qu’un principal soit accessible, et son `scope`.
- `conditions` et `blockers` : ce qui peut bloquer le chemin en pratique, comme les clés de condition, les SCP, les boundaries ou les policies d’admission.
- `confidence`, `severity`, `mitigation`, `references` et `notes` facultatif.

Les champs, types de cibles, clés de selector et espaces réservés inconnus sont rejetés plutôt qu’ignorés, afin qu’une entrée ne puisse jamais élargir ou restreindre silencieusement l’ensemble des cibles. Ajoutez d’abord la prise en charge d’un nouveau selector dans l’évaluateur du consommateur.

## Validation et synchronisation

Avant de soumettre des modifications, exécutez `python scripts/validate_privesc_paths.py --book-root .` avec PyYAML installé. Le script vérifie la structure des répertoires, chaque entrée à l’aide du chargeur strict de l’évaluateur (`scripts/privesc_paths_schema.py`, une copie du module de schéma de Blue-CloudPEASS), l’unicité des identifiants, l’existence dans ce livre de chaque page `source` et l’actualité du schéma JSON. Le workflow de pull request du livre exécute la même validation.

Chaque lundi, Blue-CloudPEASS récupère la version actuelle de `master` de ce livre, valide ces fichiers et compare le hash SHA-256 de chaque fichier aux hashs enregistrés lors de la synchronisation précédente. Les ajouts, mises à jour et suppressions en amont remplacent les copies inchangées chez le consommateur. Un fichier modifié des deux côtés est signalé comme conflit, et aucun identifiant de technique n’est supprimé sans entrée explicite et vérifiée dans le registre. Un contenu invalide ou un test en échec laisse inchangée la branche par défaut du consommateur. Les modifications sans rapport avec ces fichiers dans le livre ne génèrent aucun commit chez le consommateur.
{{#include ../banners/hacktricks-training.md}}
