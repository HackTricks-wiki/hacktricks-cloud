# Percorsi di privilege escalation

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud mantiene il catalogo leggibile automaticamente dei percorsi di privilege escalation utilizzato da [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Ogni tecnica specifica quali autorizzazioni un principal deve possedere effettivamente e su quali risorse per ottenere i privilegi di un insieme di principal target. Blue-CloudPEASS valuta queste voci offline su uno snapshot di inventario in sola lettura e traccia i percorsi di attacco da un principal all'altro, indicando come prova la policy o il binding che concede l'accesso e la mitigazione che rimuove il percorso. Modifica qui i file canonici, non le copie presenti nel consumer.

Le voci descrivono solo i prerequisiti, i target raggiungibili e la mitigazione. Non contengono comandi, payload o passaggi di esecuzione; la pagina HackTricks collegata spiega la tecnica.

## Struttura

È presente una directory per ogni piattaforma (`aws`, `gcp`, `azure`, `k8s`) e un file `<service>.yaml` per ogni servizio, ciascuno contenente un elenco YAML di tecniche. I file denominati `_excluded*.yaml` elencano le tecniche HackTricks esaminate che intenzionalmente non hanno una voce, ad esempio quelle di post-exploitation, persistence o non modellabili a partire dalla configurazione, indicando il motivo. `privesc-technique.schema.json` è lo JSON Schema esportato per il completamento automatico e la convalida nell'editor.

## Campi delle tecniche

- `id`: univoco a livello globale, in minuscolo e kebab-case, con prefisso della piattaforma.
- `provider`, `service`, `title` e `summary`: una frase che descrive ciò che ottiene la sorgente.
- `source`: la pagina e l'anchor di HackTricks che documentano la tecnica, relativi a questo libro. `source_revision` è il commit del libro consultato.
- `requires`: le autorizzazioni che la sorgente deve possedere. `all_of` elenca tutti gli elementi richiesti e `any_of` le alternative. Gli elementi AWS e GCP usano `action` e `resource`; quelli Azure usano `action` (o `data_action) e `scope`; quelli Entra ID usano `entra_permission` o `entra_role`; quelli Kubernetes usano `verb`, `resource`, `subresource`, `api_group` e `namespace`. I placeholder come `{target.arn}` associano un requisito al target.
- `target`: il `kind` del target, un `selector` le cui condizioni devono essere tutte vere affinché un principal sia raggiungibile e il relativo `scope`.
- `conditions` e `blockers`: ciò che può impedire concretamente il percorso, ad esempio condition key, SCP, boundary o policy di ammissione.
- `confidence`, `severity`, `mitigation`, `references` e `notes` opzionale.

I campi, i tipi di target, le chiavi del selector e i placeholder sconosciuti vengono rifiutati, non ignorati: in questo modo una voce non può ampliare o restringere silenziosamente l'insieme dei target. Prima aggiungi il supporto per un nuovo selector nell'evaluator del consumer.

### Join dello schema v2

Il loader v2 aggiunge due placeholder e un selector AWS, e consente l'uso del selector K8s per i pod in esecuzione sui target GCP. Questi campi richiedono un join esatto con l'inventario raccolto; se l'inventario non è disponibile, la copertura è sconosciuta e non viene indicato un percorso raggiungibile.

| Campo | Utilizzo e forma richiesta |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` e `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Usali insieme su un target AWS `aws_account_admin`. Ogni alternativa dei requisiti deve includere `iam:CreatePolicyVersion` su quel placeholder. La policy deve essere collegata a un ruolo che la sorgente può assumere nello stesso account; l'evaluator verifica la capacità delle versioni della policy e ricalcola le autorizzazioni effettive del ruolo. `SetDefaultPolicyVersion` non è supportato. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Su un target GCP `k8s_service_account` con `scope: cluster`, seleziona i KSA utilizzati da pod in esecuzione con un token disponibile nel cluster GKE corrispondente. Non combinarlo con `k8s_sa_in_cluster` o `k8s_sa_has_token_secret`. L'utilizzo esistente su K8s non cambia. |
| `{source_rolebound_clusterrole}` | Usalo come `resource_name` sui requisiti K8s `clusterroles` con `api_group: rbac.authorization.k8s.io` e `namespace: "*"`. Ogni alternativa richiede `escalate` e `update` oppure `patch` sullo stesso nome. Il target deve essere un `k8s_service_account` con `scope: same_namespace` e `selector.k8s_sa_in_namespace: "{target.namespace}"`; un RoleBinding deve associare la sorgente in quel namespace. |

## Convalida e sincronizzazione

Prima di inviare le modifiche, esegui `python scripts/validate_privesc_paths.py --book-root .` con PyYAML installato. Verifica la struttura delle directory, ogni voce tramite il loader rigoroso dell'evaluator (`scripts/privesc_paths_schema.py`, una copia del modulo dello schema di Blue-CloudPEASS), gli id univoci, le pagine sorgente e gli anchor dei titoli, nonché che lo JSON Schema sia aggiornato. Usa `--peaso-root /path/to/Blue-CloudPEASS` per confrontare anche byte per byte entrambi i file di schema con quelli del consumer. Il workflow delle pull request del libro esegue la stessa convalida.

Ogni lunedì, Blue-CloudPEASS effettua il checkout del `master` corrente di questo libro, convalida questi file e confronta l'hash SHA-256 di ciascun file con quelli registrati durante la sincronizzazione precedente. Le aggiunte, gli aggiornamenti e le eliminazioni upstream sostituiscono le copie invariate nel consumer. Un file modificato su entrambi i lati viene segnalato come conflitto e gli id delle tecniche non vengono mai eliminati senza un registro esplicito e revisionato. Contenuti non validi o un test non superato lasciano invariato il branch predefinito del consumer. Le modifiche non correlate al libro non generano commit nel consumer.
{{#include ../banners/hacktricks-training.md}}
