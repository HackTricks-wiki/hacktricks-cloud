# Categorizzazioni del rischio delle permission

HackTricks Cloud mantiene i dati condivisi sulla severity delle permission utilizzati da [CloudPEASS](https://github.com/peass-ng/CloudPEASS) e [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Modifica qui il file canonico della piattaforma, invece delle copie generate in uno dei due consumer.

- **Critical**: permission che garantiscono direttamente, o quasi indipendentemente, privilegi potenti, creano un'identità o consentono l'esecuzione privilegiata.
- **High**: accesso a informazioni sensibili, credenziali o a un percorso condizionale di privilege escalation.
- **Medium**: DoS/interruzione, interruzioni operative, modifiche ordinarie o capability condizionali senza un percorso dimostrato verso dati sensibili o privilegi.
- **Low**: attività ordinarie di discovery e accesso ai metadata.

Esiste un file YAML canonico per ogni piattaforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) e [Kubernetes](k8s.yaml). Questi sono file leggibili dalle macchine; le pagine delle piattaforme spiegano come modificarli.

## File dei cloud provider

`version` e `provider` identificano lo schema. `permission_categories` contiene i quattro elenchi individuali di permission. Sposta una permission tra gli elenchi per modificarne la valutazione. Il matching di AWS e Azure ignora il maiuscolo/minuscolo; il matching di GCP preserva il maiuscolo/minuscolo. Gli alias per il maiuscolo/minuscolo possono ripetersi all'interno della stessa severity, ma le valutazioni in conflitto vengono rifiutate.

`severity_overrides` contiene eccezioni verificate alle regole generiche. Se un'eccezione compare anche nel catalogo, entrambe le voci devono concordare. `severity_caps` impedisce a una combinazione di aumentare la valutazione di determinate permission. `non_permission_identifiers` esclude i nomi documentati dei metodi API, le condition key e altre stringhe che non sono vere permission di autorizzazione.

`combinations.critical` e `combinations.high` sono elenchi di liste di permission: ogni elemento di una lista interna deve essere concesso affinché la combinazione si applichi. Mantieni unite le combinazioni; suddividerle in grant individuali sovrastimerebbe il rischio. I campi esatti ed espressioni regolari esistenti restano il fallback per le permission assenti dal catalogo. Una riscrittura completa del classifier o un nuovo comportamento di matching richiede comunque modifiche al codice nei consumer.

## File Kubernetes

`rules` è ordinato: vince la prima regola corrispondente. Ogni regola ha un `id` univoco, un `match`, una `severity` e una `description` in linguaggio naturale. Aggiungi una regola più specifica prima di una più generica oppure modifica la severity di una regola esistente. Mantieni il fallback finale incondizionato.

I match usano `all`, `any` e `not` per la composizione, oppure un confronto `field`, `op` e `value`. I campi disponibili sono `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL non-resource in lowercase), `non_resource_url`, `mode` e `delegated_verb`. Le operazioni sono `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` e `truthy` (non richiede un valore). `always: true` corrisponde a tutto. I valori di group, resource, subresource e verb sono in lowercase. Un wildcard letterale viene scritto come `'*'`; il matching di un grant wildcard è esplicito nelle regole, invece di usare l'espansione dei pattern della shell.

`severity_when` seleziona facoltativamente un'altra severity per una condizione corrispondente. `severity: delegated` è riservato all'impersonation vincolata: la sua mappa `delegated_severities` converte la classificazione dell'azione delegata nella valutazione condizionale. I placeholder della description possono fare riferimento ai campi disponibili, come `{full}` e `{verb}`. Le regole sono dati e non vengono mai valutate come codice Python o shell.

## Validazione e sincronizzazione

Esegui `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` con PyYAML installato prima di inviare le modifiche. Il workflow delle pull request del book esegue la stessa validazione.

Ogni lunedì, entrambi i repository consumer effettuano il checkout dell'attuale `master` di questo book, validano tutti e quattro i file, confrontano gli hash SHA-256 e aggiornano i loro file YAML inclusi e gli elenchi legacy generati. Un manifest dei sorgenti registra la revisione del book e l'hash di ciascun file. Le modifiche non correlate al book non producono alcun commit nel consumer. Ogni workflow supporta anche un'esecuzione manuale. I test vengono eseguiti prima che il workflow esegua il commit dei dati modificati nel branch predefinito del consumer; gli errori lasciano quel branch invariato. I consumer continuano a utilizzare offline le loro copie incluse tra un aggiornamento e l'altro.

Per aggiornare localmente un consumer, esegui `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Aggiungi `--check` per rilevare le copie obsolete senza modificarle.
