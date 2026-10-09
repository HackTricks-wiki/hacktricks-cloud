# Categorizzazioni del rischio delle autorizzazioni

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud gestisce i dati condivisi sulla gravità delle autorizzazioni utilizzati da [CloudPEASS](https://github.com/peass-ng/CloudPEASS) e [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Modifica qui il file canonico della piattaforma, anziché le copie generate nei due consumer.

- **Critical**: autorizzazioni che concedono direttamente, o quasi autonomamente, privilegi elevati, creano un'identità o consentono l'esecuzione con privilegi elevati.
- **High**: accesso a informazioni sensibili o credenziali, oppure un percorso condizionale di escalation dei privilegi.
- **Medium**: DoS/Break, interruzione operativa, modifiche ordinarie o funzionalità condizionali senza un percorso dimostrato verso dati sensibili o privilegi.
- **Low**: normale individuazione e accesso ai metadati.

Esiste un file YAML canonico per ogni piattaforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) e [Kubernetes](k8s.yaml). Sono file leggibili dalle macchine; le pagine delle piattaforme mostrano il loro YAML completo nel browser e spiegano come modificarli. Il visualizzatore integrato usa la copia del libro, mentre i workflow di PEASS recuperano i file canonici da GitHub.

## File dei provider cloud

`version` e `provider` identificano lo schema. `permission_categories` contiene i quattro elenchi di autorizzazioni. Sposta un'autorizzazione tra gli elenchi per modificarne la classificazione. La corrispondenza di AWS e Azure ignora le maiuscole; quella di GCP le distingue. Gli alias che differiscono solo per maiuscole e minuscole possono ripetersi all'interno della stessa categoria di gravità, ma le classificazioni in conflitto vengono rifiutate.

`severity_overrides` contiene eccezioni verificate alle regole generiche. Se un'eccezione compare anche nel catalogo, le due voci devono concordare. `severity_caps` impedisce a una combinazione di innalzare la classificazione delle autorizzazioni selezionate. `non_permission_identifiers` esclude i nomi documentati dei metodi API, le condition key e altre stringhe che non sono autorizzazioni di autorizzazione effettive.

`combinations.critical` e `combinations.high` sono elenchi di elenchi di autorizzazioni: per applicare una combinazione devono essere concesse tutte le autorizzazioni di un elenco interno. Mantieni unite le combinazioni; suddividerle in singole concessioni sovrastimerebbe il rischio. I campi esistenti per le corrispondenze esatte e le espressioni regolari restano il fallback per le autorizzazioni assenti dal catalogo. Una riscrittura completa del classificatore o l'introduzione di un nuovo comportamento di corrispondenza richiede comunque modifiche al codice dei consumer.

## File Kubernetes

`rules` è ordinato: prevale la prima regola corrispondente. Ogni regola ha un `id` univoco, un `match`, una `severity` e una `description` in linguaggio naturale. Aggiungi una regola più specifica prima di una più ampia oppure modifica la gravità di una regola esistente. Mantieni il fallback finale incondizionato.

Le corrispondenze usano `all`, `any` e `not` per la composizione, oppure un confronto `field`, `op` e `value`. I campi disponibili sono `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL non-resource in minuscolo), `non_resource_url`, `mode` e `delegated_verb`. Le operazioni sono `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` e `truthy` (non richiede un valore). `always: true` corrisponde a tutto. I valori di group, resource, subresource e verb sono in minuscolo. Un wildcard letterale si scrive `'*'`; la corrispondenza con una concessione wildcard è esplicita nelle regole, anziché basarsi sull'espansione dei pattern della shell.

`severity_when` seleziona facoltativamente un'altra gravità per una condizione corrispondente. `severity: delegated` è riservato all'impersonation vincolata: la sua mappa `delegated_severities` converte la classificazione dell'azione delegata nella valutazione condizionale. I segnaposto della descrizione possono fare riferimento ai campi disponibili, come `{full}` e `{verb}`. Le regole sono dati e non vengono mai eseguite come codice Python o shell.

## Convalida e sincronizzazione

Prima di inviare le modifiche, esegui `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` con PyYAML installato. Il workflow delle pull request del libro esegue la stessa convalida.

Ogni lunedì, entrambi i repository consumer estraggono il `master` corrente di questo libro, convalidano tutti e quattro i file, confrontano gli hash SHA-256 e aggiornano i file YAML inclusi e gli elenchi legacy generati. Un manifest sorgente registra la revisione del libro e l'hash di ciascun file. Le modifiche non correlate al libro non generano commit nei consumer. Ogni workflow supporta anche l'esecuzione manuale. I test vengono eseguiti prima che il workflow esegua il commit dei dati modificati nel branch predefinito del consumer; in caso di errore, quel branch rimane invariato. Tra un aggiornamento e l'altro, i consumer continuano a usare le copie incluse, anche offline.

Per aggiornare localmente un consumer, esegui `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Aggiungi `--check` per rilevare le copie non aggiornate senza modificarle.

Il recupero dei sorgenti in entrambi i consumer riprova cinque volte, con scadenze di checkout limitate e ritardi crescenti. I download incompleti restano in directory temporanee; se i tentativi si esauriscono, i dati inclusi esistenti rimangono invariati.
{{#include ../banners/hacktricks-training.md}}
