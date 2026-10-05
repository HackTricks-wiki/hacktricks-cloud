# Κατηγοριοποιήσεις κινδύνου permissions

Το HackTricks Cloud διατηρεί τα κοινόχρηστα δεδομένα severity των permissions που χρησιμοποιούνται από τα [CloudPEASS](https://github.com/peass-ng/CloudPEASS) και [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Επεξεργαστείτε εδώ το canonical αρχείο της πλατφόρμας, αντί για τα generated αντίγραφα σε οποιονδήποτε από τους δύο consumers.

- **Critical**: permissions που παρέχουν άμεσα ή σχεδόν ανεξάρτητα ισχυρά privileges, δημιουργούν μια identity ή επιτρέπουν privileged execution.
- **High**: πρόσβαση σε ευαίσθητες πληροφορίες, credentials ή σε conditional privilege escalation path.
- **Medium**: DoS/Break, operational disruption, συνηθισμένες αλλαγές ή conditional capabilities χωρίς αποδεδειγμένο sensitive-data ή privilege path.
- **Low**: συνηθισμένο discovery και πρόσβαση σε metadata.

Υπάρχει ένα canonical YAML αρχείο ανά platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) και [Kubernetes](k8s.yaml). Αυτά είναι machine-readable αρχεία· οι σελίδες των platforms εμφανίζουν το πλήρες YAML στον browser και εξηγούν πώς να το επεξεργαστείτε. Ο inline viewer χρησιμοποιεί το αντίγραφο του βιβλίου, ενώ τα PEASS workflows ανακτούν τα canonical αρχεία από το GitHub.

## Cloud provider files

Τα `version` και `provider` προσδιορίζουν το schema. Το `permission_categories` περιέχει τις τέσσερις μεμονωμένες permission lists. Μετακινήστε ένα permission μεταξύ των lists για να αλλάξετε το rating του. Το matching σε AWS και Azure αγνοεί το case· το matching σε GCP διατηρεί το case. Τα case aliases μπορούν να επαναλαμβάνονται μέσα στο ίδιο severity, αλλά απορρίπτονται conflicting ratings.

Το `severity_overrides` περιέχει audited exceptions σε generic rules. Αν μια exception εμφανίζεται επίσης στον catalog, και οι δύο καταχωρίσεις πρέπει να συμφωνούν. Το `severity_caps` αποτρέπει την αναβάθμιση επιλεγμένων permissions από έναν συνδυασμό. Το `non_permission_identifiers` εξαιρεί τεκμηριωμένα API-method names, condition keys και άλλα strings που δεν είναι πραγματικά authorization permissions.

Τα `combinations.critical` και `combinations.high` είναι lists από permission lists: κάθε στοιχείο μιας εσωτερικής list πρέπει να έχει granted ώστε να ισχύει ο συγκεκριμένος συνδυασμός. Διατηρείτε τους συνδυασμούς ενωμένους· ο διαχωρισμός τους σε μεμονωμένα grants θα υπερεκτιμούσε τον κίνδυνο. Τα υπάρχοντα exact και regular-expression fields παραμένουν το fallback για permissions που απουσιάζουν από τον catalog. Μια πλήρης επανεγγραφή του classifier ή νέα matching behavior εξακολουθεί να απαιτεί αλλαγές κώδικα στους consumers.

## Kubernetes file

Το `rules` είναι ordered: ισχύει ο πρώτος κανόνας που κάνει match. Κάθε rule έχει ένα μοναδικό `id`, ένα `match`, ένα `severity` και ένα `description` σε απλή γλώσσα. Προσθέστε ένα πιο συγκεκριμένο rule πριν από ένα ευρύτερο ή αλλάξτε το severity ενός υπάρχοντος rule. Διατηρήστε το τελικό unconditional fallback.

Τα matches χρησιμοποιούν `all`, `any` και `not` για composition ή μια σύγκριση `field`, `op` και `value`. Τα διαθέσιμα fields είναι `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode` και `delegated_verb`. Οι operations είναι `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` και `truthy` (δεν απαιτείται value). Το `always: true` κάνει match σε όλα. Οι τιμές των group, resource, subresource και verb είναι lowercase. Ένα literal wildcard γράφεται ως `'*'`· το matching ενός wildcard grant είναι explicit στα rules και όχι shell pattern expansion.

Το `severity_when` επιλέγει προαιρετικά ένα άλλο severity για μια matching condition. Το `severity: delegated` προορίζεται αποκλειστικά για constrained impersonation: το `delegated_severities` map του μετατρέπει το classification της delegated action σε conditional rating. Τα placeholders του description μπορούν να αναφέρονται στα διαθέσιμα fields, όπως `{full}` και `{verb}`. Τα rules είναι data και δεν αξιολογούνται ποτέ ως Python ή shell code.

## Validation and synchronization

Εκτελέστε `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` με εγκατεστημένο το PyYAML πριν υποβάλετε αλλαγές. Το pull-request workflow του βιβλίου εκτελεί την ίδια validation.

Κάθε Δευτέρα, και τα δύο consumer repositories κάνουν checkout το τρέχον `master` αυτού του βιβλίου, κάνουν validation και των τεσσάρων αρχείων, συγκρίνουν SHA-256 hashes και ενημερώνουν τα bundled YAML αρχεία τους και τις generated legacy lists. Ένα source manifest καταγράφει το revision του βιβλίου και το hash κάθε αρχείου. Άσχετες αλλαγές στο βιβλίο δεν δημιουργούν consumer commit. Κάθε workflow υποστηρίζει επίσης manual run. Τα tests εκτελούνται πριν το workflow κάνει commit των αλλαγμένων data στο default branch του consumer· αποτυχίες αφήνουν αυτό το branch αμετάβλητο. Οι consumers συνεχίζουν να χρησιμοποιούν τα bundled αντίγραφά τους offline μεταξύ των updates.

Για τοπική ενημέρωση σε έναν consumer, εκτελέστε `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Προσθέστε `--check` για να εντοπίσετε stale αντίγραφα χωρίς να τα γράψετε.

Το source fetching και στους δύο consumers κάνει retry πέντε φορές, με bounded checkout deadlines και αυξανόμενες καθυστερήσεις. Οι incomplete downloads παραμένουν σε προσωρινούς καταλόγους· όταν εξαντληθούν τα retries, τα υπάρχοντα bundled data παραμένουν αμετάβλητα.
