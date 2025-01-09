# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks λογότυπα & κίνηση σχεδιασμένα από_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Εκτέλεση του HackTricks Cloud Τοπικά
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Η τοπική σας έκδοση του HackTricks Cloud θα είναι **διαθέσιμη στο [http://localhost:3377](http://localhost:3377)** μετά από ένα λεπτό.

### **Μεθοδολογία Pentesting CI/CD**

**Στη Μεθοδολογία CI/CD του HackTricks θα βρείτε πώς να κάνετε pentest υποδομές που σχετίζονται με δραστηριότητες CI/CD.** Διαβάστε την παρακάτω σελίδα για μια **εισαγωγή:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Μεθοδολογία Pentesting Cloud

**Στη Μεθοδολογία Cloud του HackTricks θα βρείτε πώς να κάνετε pentest σε περιβάλλοντα cloud.** Διαβάστε την παρακάτω σελίδα για μια **εισαγωγή:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Άδεια & Αποποίηση Ευθύνης

**Ελέγξτε τα εδώ:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Στατιστικά Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
