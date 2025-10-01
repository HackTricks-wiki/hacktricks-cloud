# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Τα λογότυπα και η κινούμενη εικόνα του Hacktricks σχεδιάστηκαν από_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Τρέξτε το HackTricks Cloud τοπικά
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud

# Select the language you want to use
export LANG="master" # Leave master for English
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
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Το τοπικό σας αντίγραφο του HackTricks Cloud θα είναι **διαθέσιμο στο [http://localhost:3377](http://localhost:3377)** μέσα σε ένα λεπτό.

### **Pentesting CI/CD Μεθοδολογία**

**Στη HackTricks CI/CD Μεθοδολογία θα βρείτε πώς να pentest την υποδομή που σχετίζεται με δραστηριότητες CI/CD.** Διαβάστε την παρακάτω σελίδα για μια **εισαγωγή:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Μεθοδολογία

**Στην HackTricks Cloud Μεθοδολογία θα βρείτε πώς να pentest περιβάλλοντα cloud.** Διαβάστε την παρακάτω σελίδα για μια **εισαγωγή:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Άδεια & Αποποίηση

**Ελέγξτε τα στο:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Στατιστικά

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
