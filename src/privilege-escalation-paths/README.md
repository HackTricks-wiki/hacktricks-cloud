# Chemins d’escalade de privilèges

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud gère le catalogue des chemins d’escalade de privilèges lisible par machine, utilisé par [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Chaque technique indique les permissions qu’un principal doit effectivement détenir, et sur quelles ressources, pour obtenir les privilèges d’un ensemble de principaux cibles. Blue-CloudPEASS évalue ces entrées hors ligne à partir d’un instantané d’inventaire en lecture seule et dessine les chemins d’attaque entre principaux, en indiquant comme preuve la stratégie ou la liaison qui accorde les permissions, ainsi que la mesure corrective qui supprime le chemin. Modifiez ici les fichiers canoniques, et non les copies utilisées par le consommateur.

Les entrées décrivent uniquement les conditions préalables, les cibles accessibles et les mesures correctives. Elles ne contiennent ni commandes, ni payloads, ni étapes d’exécution ; la page HackTricks liée explique la technique.

## Organisation

Il existe un répertoire par plateforme (`aws`, `gcp`, `azure`, `k8s`) et un fichier `<service>.yaml` par service, chacun contenant une liste YAML de techniques. Les fichiers nommés `_excluded*.yaml` répertorient les techniques HackTricks examinées qui n’ont volontairement pas d’entrée, par exemple celles concernant le post-exploitation, la persistence ou les techniques qui ne peuvent pas être modélisées à partir de la configuration, avec la raison correspondante. `privesc-technique.schema.json` est le JSON Schema exporté pour la complétion et la validation dans l’éditeur.

## Champs des techniques

- `id` : unique globalement, en minuscules et au format kebab-case, préfixé par la plateforme.
- `provider`, `service`, `title` et `summary` : une phrase décrivant ce que la source obtient.
- `source` : page HackTricks et ancre documentant la technique, relatives à ce livre. `source_revision` est le commit du livre consulté.
- `requires` : les permissions que la source doit détenir. `all_of` répertorie tous les éléments requis et `any_of` les alternatives. Les éléments AWS et GCP utilisent `action` et `resource`, les éléments Azure utilisent `action` (ou `data_action`) et `scope`, les éléments Entra ID utilisent `entra_permission` ou `entra_role`, et les éléments Kubernetes utilisent `verb`, `resource`, `subresource`, `api_group` et `namespace`. Les placeholders tels que `{target.arn}` associent une exigence à la cible.
- `target` : le `kind` de la cible, un `selector` dont toutes les conditions doivent être remplies pour qu’un principal soit accessible, ainsi que son `scope`.
- `conditions` et `blockers` : les éléments susceptibles d’empêcher le chemin en pratique, comme les clés de condition, les SCP, les limites ou les stratégies d’admission.
- `confidence`, `severity`, `mitigation`, `references` et `notes` facultatives.

Les champs, types de cibles, clés de sélecteur et placeholders inconnus sont rejetés plutôt qu’ignorés : une entrée ne peut donc jamais élargir ou réduire silencieusement l’ensemble de ses cibles. Ajoutez d’abord la prise en charge d’un nouveau sélecteur dans l’évaluateur du consommateur.

### Jointures du schéma v2

Le chargeur v2 ajoute deux placeholders et un sélecteur AWS, et autorise le sélecteur K8s existant `running-pod` pour les cibles GCP. Ces champs nécessitent une jointure exacte avec l’inventaire collecté ; si l’inventaire est manquant, la couverture est inconnue et aucun chemin accessible n’est indiqué.

| Champ | Utilisation et forme requise |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` et `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | À utiliser ensemble sur une cible AWS `aws_account_admin`. Chaque alternative d’exigence doit inclure `iam:CreatePolicyVersion` sur ce placeholder. La stratégie doit être attachée à un rôle que la source peut assumer dans le même compte ; l’évaluateur vérifie la capacité de versionnement de la stratégie et recalcule les permissions effectives du rôle. `SetDefaultPolicyVersion` n’est pas pris en charge. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Sur une cible GCP `k8s_service_account` avec `scope: cluster`, sélectionne les KSA utilisés par des pods en cours d’exécution disposant d’un token disponible dans le cluster GKE correspondant. Ne le combinez pas avec `k8s_sa_in_cluster` ou `k8s_sa_has_token_secret`. L’utilisation existante sur K8s reste inchangée. |
| `{source_rolebound_clusterrole}` | À utiliser comme `resource_name` pour les exigences K8s `clusterroles` avec `api_group: rbac.authorization.k8s.io` et `namespace: "*"`. Chaque alternative nécessite `escalate` et `update` ou `patch` sur le même nom. La cible doit être un `k8s_service_account` avec `scope: same_namespace` et `selector.k8s_sa_in_namespace: "{target.namespace}"` ; un RoleBinding doit lier la source dans cet espace de noms. |

## Validation et synchronisation

Avant de soumettre des modifications, exécutez `python scripts/validate_privesc_paths.py --book-root .` avec PyYAML installé. Ce script vérifie l’organisation des répertoires, chaque entrée à l’aide du chargeur strict de l’évaluateur (`scripts/privesc_paths_schema.py`, une copie du module de schéma de Blue-CloudPEASS), l’unicité des identifiants, les pages source et les ancres de titre, ainsi que l’actualité du JSON Schema. Utilisez `--peaso-root /path/to/Blue-CloudPEASS` pour comparer également, octet par octet, les deux fichiers de schéma à ceux du consommateur. Le workflow de pull request du livre exécute la même validation.

Chaque lundi, Blue-CloudPEASS récupère la version actuelle de `master` de ce livre, valide ces fichiers et compare le SHA-256 de chaque fichier aux hachages enregistrés lors de la synchronisation précédente. Les ajouts, mises à jour et suppressions en amont remplacent les copies inchangées du consommateur. Un fichier modifié des deux côtés est signalé comme conflit, et les identifiants de technique ne sont jamais supprimés sans entrée explicite dans le registre ayant fait l’objet d’une revue. Un contenu invalide ou un test échoué laisse la branche par défaut du consommateur inchangée. Les modifications sans rapport dans le livre ne produisent aucun commit chez le consommateur.
{{#include ../banners/hacktricks-training.md}}
