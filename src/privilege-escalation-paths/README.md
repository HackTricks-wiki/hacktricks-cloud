# Percorsi di privilege escalation

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud mantiene il catalogo machine-readable delle tecniche di privilege escalation utilizzato da [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Ogni tecnica specifica quali permessi un principal deve effettivamente possedere e su quali risorse per ottenere i privilegi di un insieme di principal target. Blue-CloudPEASS valuta queste voci offline su uno snapshot di inventario in sola lettura e traccia i percorsi di attacco da principal a principal, indicando come prova la policy o il binding che concede i permessi e la mitigazione che elimina il percorso. Modifica i file canonici qui, anziché le copie presenti nel consumer.

Le voci descrivono solo i prerequisiti, i target raggiungibili e la mitigazione. Non contengono comandi, payload o passaggi di esecuzione; la pagina HackTricks collegata spiega la tecnica.

## Struttura

C'è una directory per ogni piattaforma (`aws`, `gcp`, `azure`, `k8s`) e un file `<service>.yaml` per ogni servizio, ciascuno contenente un elenco YAML di tecniche. I file chiamati `_excluded*.yaml` elencano le tecniche HackTricks esaminate che intenzionalmente non hanno una voce, come quelle di post-exploitation, persistence o non modellabili dalla configurazione, insieme alla motivazione. `privesc-technique.schema.json` è lo schema JSON esportato per il completamento automatico e la convalida nell'editor.

## Campi delle tecniche

- `id`: identificatore univoco a livello globale, in minuscolo e kebab-case, con prefisso della piattaforma.
- `provider`, `service`, `title` e `summary`: una frase che descrive cosa ottiene la fonte.
- `source`: la pagina e l'anchor HackTricks che documentano la tecnica, relativi a questo libro. `source_revision` è il commit del libro consultato.
- `requires`: i permessi che la fonte deve possedere. `all_of` elenca tutti gli elementi richiesti e `any_of` le alternative. Gli elementi AWS e GCP usano `action` e `resource`; quelli Azure usano `action` (o `data_action`) e `scope`; quelli Entra ID usano `entra_permission` o `entra_role`; quelli Kubernetes usano `verb`, `resource`, `subresource`, `api_group` e `namespace`. I placeholder come `{target.arn}` associano un requisito al target.
- `target`: il `kind` del target, un `selector` le cui condizioni devono essere tutte soddisfatte affinché un principal sia raggiungibile e il suo `scope`.
- `conditions` e `blockers`: ciò che può impedire il percorso nella pratica, come condition key, SCP, boundaries o policy di admission.
- `confidence`, `severity`, `mitigation`, `references` e `notes` facoltativo.

I campi, i tipi di target, le chiavi di selector e i placeholder sconosciuti vengono rifiutati anziché ignorati, così una voce non può mai ampliare o restringere silenziosamente l'insieme dei target. Aggiungi prima il supporto per un nuovo selector nell'evaluator del consumer.

## Convalida e sincronizzazione

Prima di inviare modifiche, esegui `python scripts/validate_privesc_paths.py --book-root .` con PyYAML installato. Lo script controlla la struttura delle directory, ogni voce con il loader rigoroso dell'evaluator (`scripts/privesc_paths_schema.py`, una copia del modulo schema di Blue-CloudPEASS), l'univocità degli id, l'esistenza in questo libro di ogni pagina `source` e che lo schema JSON sia aggiornato. Il workflow delle pull request del libro esegue la stessa convalida.

Ogni lunedì, Blue-CloudPEASS esegue il checkout del `master` corrente di questo libro, convalida questi file e confronta l'hash SHA-256 di ciascun file con gli hash registrati durante la sincronizzazione precedente. Le aggiunte, gli aggiornamenti e le eliminazioni upstream sostituiscono le copie invariate nel consumer. Se un file è stato modificato su entrambi i lati, viene segnalato un conflitto; gli id delle tecniche non vengono mai rimossi senza un ledger esplicito e verificato. Contenuti non validi o un test fallito lasciano invariato il branch predefinito del consumer. Le modifiche non correlate al libro non producono commit nel consumer.
{{#include ../banners/hacktricks-training.md}}
