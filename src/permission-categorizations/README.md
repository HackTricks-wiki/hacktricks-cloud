# Κατηγοριοποιήσεις κινδύνου permissions

Το HackTricks Cloud διατηρεί τα κοινόχρηστα δεδομένα severity των permissions που χρησιμοποιούνται από τα [CloudPEASS](https://github.com/peass-ng/CloudPEASS) και [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Επεξεργαστείτε το canonical platform file εδώ, αντί για τα generated copies σε οποιονδήποτε consumer.

- **Critical**: permissions που παρέχουν άμεσα ή σχεδόν ανεξάρτητα ισχυρά privileges, δημιουργούν μια identity ή επιτρέπουν privileged execution.
- **High**: πρόσβαση σε sensitive information, credentials ή conditional privilege escalation path.
- **Medium**: DoS/Break, operational disruption, ordinary changes ή conditional capabilities χωρίς demonstrated sensitive-data ή privilege path.
- **Low**: ordinary discovery και πρόσβαση σε metadata.

Υπάρχει ένα canonical YAML file ανά platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) και [Kubernetes](k8s.yaml). Αυτά είναι machine-readable files· οι σελίδες των platforms εξηγούν πώς να τα επεξεργαστείτε.

## Cloud provider files

Τα `version` και `provider` προσδιορίζουν το schema. Το `permission_categories` περιέχει τις τέσσερις individual permission lists. Μετακινήστε ένα permission μεταξύ των lists για να αλλάξετε το rating του. Το matching σε AWS και Azure αγνοεί το case· το matching σε GCP διατηρεί το case. Τα case aliases μπορούν να επαναλαμβάνονται μέσα στο ίδιο severity, αλλά τα conflicting ratings απορρίπτονται.

Το `severity_overrides` περιέχει audited exceptions στους generic rules. Αν ένα exception εμφανίζεται επίσης στο catalog, και οι δύο entries πρέπει να συμφωνούν. Το `severity_caps` αποτρέπει έναν συνδυασμό από το να αναβαθμίσει επιλεγμένα permissions. Το `non_permission_identifiers` εξαιρεί documented API-method names, condition keys και άλλα strings που δεν είναι πραγματικά authorization permissions.

Τα `combinations.critical` και `combinations.high` είναι lists από permission lists: κάθε element μιας inner list πρέπει να έχει granted για να εφαρμοστεί ο συγκεκριμένος συνδυασμός. Διατηρήστε τους συνδυασμούς μαζί· ο διαχωρισμός τους σε individual grants θα υπερεκτιμούσε τον κίνδυνο. Τα υπάρχοντα exact και regular-expression fields παραμένουν το fallback για permissions που απουσιάζουν από το catalog. Ένα πλήρες classifier rewrite ή νέα matching behavior εξακολουθεί να απαιτεί code changes στους consumers.

## Kubernetes file

Το `rules` είναι ordered: εφαρμόζεται ο πρώτος matching rule. Κάθε rule έχει ένα μοναδικό `id`, ένα `match`, ένα `severity` και ένα plain-language `description`. Προσθέστε έναν πιο specific rule πριν από έναν broader ή αλλάξτε το severity ενός υπάρχοντος rule. Διατηρήστε το τελικό unconditional fallback.

Τα matches χρησιμοποιούν `all`, `any` και `not` για composition ή μια σύγκριση `field`, `op` και `value`. Τα διαθέσιμα fields είναι `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode` και `delegated_verb`. Οι operations είναι `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` και `truthy` (δεν απαιτείται value). Το `always: true` κάνει match σε όλα. Οι τιμές των group, resource, subresource και verb είναι lowercase. Ένα literal wildcard γράφεται ως `'*'`· το matching ενός wildcard grant είναι explicit στους rules, αντί για shell pattern expansion.

Το `severity_when` επιλέγει προαιρετικά ένα άλλο severity για μια matching condition. Το `severity: delegated` προορίζεται αποκλειστικά για constrained impersonation: το `delegated_severities` map μετατρέπει την classification του delegated action στο conditional rating. Τα description placeholders μπορούν να αναφέρονται στα διαθέσιμα fields, όπως `{full}` και `{verb}`. Οι rules είναι data και δεν αξιολογούνται ποτέ ως Python ή shell code.

## Validation and synchronization

Εκτελέστε `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` με εγκατεστημένο το PyYAML πριν υποβάλετε αλλαγές. Το pull-request workflow του book εκτελεί το ίδιο validation.

Κάθε Δευτέρα, και τα δύο consumer repositories κάνουν checkout το τρέχον `master` αυτού του book, κάνουν validate και τα τέσσερα files, συγκρίνουν SHA-256 hashes και ενημερώνουν τα bundled YAML files και τις generated legacy lists. Ένα source manifest καταγράφει το book revision και το hash κάθε file. Άσχετες αλλαγές στο book δεν δημιουργούν consumer commit. Κάθε workflow υποστηρίζει επίσης manual run. Τα tests εκτελούνται πριν το workflow κάνει commit των changed data στο default branch του consumer· αποτυχίες αφήνουν αυτό το branch αμετάβλητο. Οι consumers συνεχίζουν να χρησιμοποιούν τα bundled copies offline μεταξύ των updates.

Για τοπικό update σε έναν consumer, εκτελέστε `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Προσθέστε `--check` για να εντοπίσετε stale copies χωρίς να τις γράψετε.
