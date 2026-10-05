# Categorie di rischio delle permissions

HackTricks Cloud mantiene i dati condivisi sulla severity delle permissions utilizzati da [CloudPEASS](https://github.com/peass-ng/CloudPEASS) e [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Modifica qui il file canonico della piattaforma, invece delle copie generate in uno dei due consumer.

- **Critical**: permissions che concedono direttamente, o quasi indipendentemente, privilegi potenti, creano un'identità o consentono l'esecuzione privilegiata.
- **High**: accesso a informazioni sensibili, credenziali o a un percorso condizionale di privilege escalation.
- **Medium**: DoS/Break, interruzione operativa, modifiche ordinarie o capabilities condizionali senza un percorso dimostrato verso dati sensibili o privilegi.
- **Low**: discovery ordinaria e accesso ai metadati.

Esiste un file YAML canonico per ogni piattaforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) e [Kubernetes](k8s.yaml). Questi sono file leggibili dalle macchine; le pagine delle piattaforme mostrano il loro YAML completo nel browser e spiegano come modificarli. Il visualizzatore inline utilizza la copia del libro, mentre i workflow di PEASS recuperano i file canonici da GitHub.

## File dei cloud provider

`version` e `provider` identificano lo schema. `permission_categories` contiene i quattro elenchi individuali di permissions. Sposta una permission tra gli elenchi per modificarne il rating. La ricerca di corrispondenze in AWS e Azure ignora il maiuscolo/minuscolo; quella in GCP conserva il maiuscolo/minuscolo. Gli alias con differenze di maiuscole/minuscole possono ripetersi all'interno della stessa severity, ma i rating in conflitto vengono rifiutati.

`severity_overrides` contiene eccezioni verificate alle regole generiche. Se un'eccezione compare anche nel catalogo, entrambe le voci devono concordare. `severity_caps` impedisce a una combinazione di aumentare il livello delle permissions selezionate. `non_permission_identifiers` esclude i nomi documentati dei metodi API, le chiavi di condizione e altre stringhe che non sono permissions effettive di autorizzazione.

`combinations.critical` e `combinations.high` sono elenchi di elenchi di permissions: ogni elemento di un elenco interno deve essere concesso affinché la combinazione si applichi. Mantieni unite le combinazioni; dividerle in grant individuali sovrastimerebbe il rischio. I campi esistenti esatti e basati su regular expression rimangono il fallback per le permissions assenti dal catalogo. Una riscrittura completa del classifier o un nuovo comportamento di matching richiedono comunque modifiche al codice nei consumer.

## File Kubernetes

`rules` è ordinato: prevale la prima regola corrispondente. Ogni regola ha un `id` univoco, un `match`, una `severity` e una `description` in linguaggio naturale. Aggiungi una regola più specifica prima di una più generale oppure modifica la severity di una regola esistente. Mantieni il fallback incondizionato finale.

I match utilizzano `all`, `any` e `not` per la composizione, oppure un confronto tra `field`, `op` e `value`. I campi disponibili sono `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL non-resource in minuscolo), `non_resource_url`, `mode` e `delegated_verb`. Le operazioni sono `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` e `truthy` (non richiede un valore). `always: true` corrisponde a tutto. I valori di group, resource, subresource e verb sono in minuscolo. Un wildcard letterale è scritto come `'*'`; la corrispondenza con un grant wildcard è esplicita nelle regole, invece di utilizzare l'espansione dei pattern della shell.

`severity_when` seleziona facoltativamente un'altra severity per una condizione corrispondente. `severity: delegated` è riservato all'impersonation vincolata: la sua mappa `delegated_severities` converte la classificazione dell'azione delegata nel rating condizionale. I placeholder della description possono fare riferimento ai campi disponibili, come `{full}` e `{verb}`. Le regole sono dati e non vengono mai valutate come codice Python o shell.

## Validazione e sincronizzazione

Esegui `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` con PyYAML installato prima di inviare le modifiche. Il workflow di pull request del libro esegue la stessa validazione.

Ogni lunedì, entrambi i repository consumer fanno checkout del `master` corrente di questo libro, validano tutti e quattro i file, confrontano gli hash SHA-256 e aggiornano i file YAML inclusi e gli elenchi legacy generati. Un manifest delle sorgenti registra la revisione del libro e l'hash di ogni file. Le modifiche non correlate al libro non producono alcun commit nel consumer. Ogni workflow supporta anche un'esecuzione manuale. I test vengono eseguiti prima che il workflow effettui il commit dei dati modificati nel branch predefinito del consumer; gli errori lasciano quel branch invariato. I consumer continuano a utilizzare offline le proprie copie incluse tra un aggiornamento e l'altro.

Per aggiornare localmente un consumer, esegui `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Aggiungi `--check` per rilevare le copie obsolete senza scriverle.

Il recupero delle sorgenti in entrambi i consumer effettua cinque tentativi con deadline limitate per il checkout e ritardi crescenti. I download incompleti rimangono in directory temporanee; se i tentativi si esauriscono, i dati inclusi esistenti rimangono invariati.
