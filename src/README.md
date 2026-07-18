# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Τα λογότυπα και το motion του Hacktricks σχεδιάστηκαν από_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Εκτέλεση του HackTricks Cloud τοπικά
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud

# Select the language you want to use
export HT_LANG="master" # Leave master for English
# "af" for Afrikaans
# "de" for German
# "el" for Greek
# "es" for Spanish
# "fr" for French
# "hi" for Hindi
# "it" for Italian
# "ja" for Japanese
# "ko" for Korean
# "pl" for Polish
# "pt" for Portuguese
# "sr" for Serbian
# "sw" for Swahili
# "tr" for Turkish
# "uk" for Ukrainian
# "zh" for Chinese

# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $HT_LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Το τοπικό αντίγραφο του HackTricks Cloud θα είναι **διαθέσιμο στη διεύθυνση [http://localhost:3377](http://localhost:3377)** μετά από ένα λεπτό.

Εναλλακτικά, αν διαθέτετε Docker Compose, εκτελέστε το από τον ριζικό κατάλογο του repository:
```bash
docker compose up
```
Το συνοδευτικό `docker-compose.yml` εξυπηρετεί το branch που έχετε κάνει checkout στη διεύθυνση [http://localhost:3377](http://localhost:3377) με live reload.

### **Μεθοδολογία Pentesting CI/CD**

**Στη HackTricks CI/CD Methodology θα βρείτε πώς να κάνετε pentest σε υποδομές που σχετίζονται με δραστηριότητες CI/CD.** Διαβάστε την ακόλουθη σελίδα για μια **εισαγωγή:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Μεθοδολογία Pentesting Cloud

**Στη HackTricks Cloud Methodology θα βρείτε πώς να κάνετε pentest σε cloud environments.** Διαβάστε την ακόλουθη σελίδα για μια **εισαγωγή:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Άδεια χρήσης και Αποποίηση ευθύνης

**Δείτε τα εδώ:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Στατιστικά Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
