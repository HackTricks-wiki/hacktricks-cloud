# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Τα λογότυπα και η κίνηση του Hacktricks σχεδιάστηκαν από_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### Εκτέλεση του HackTricks Cloud τοπικά

Η παρακάτω ροή εργασίας ακολουθεί τις τεκμηριωμένες από το Git λειτουργίες `clone`, `checkout` και `pull`, καθώς και τα δημοσιευμένα language branches και τη ρύθμιση container του repository. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Η εντολή container ακολουθεί το τεκμηριωμένο interface `run` του Docker και χρησιμοποιεί τον HTTP preview server του mdBook· το repository αντιστοιχίζει τη θύρα 3000 του container στην τοπική θύρα 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Το τοπικό αντίγραφο του HackTricks Cloud θα είναι **διαθέσιμο στη διεύθυνση [http://localhost:3377](http://localhost:3377)** μετά από ένα λεπτό. <sup>[[3]](#references)</sup>

Εναλλακτικά, αν έχετε Docker Compose, εκτελέστε το εξής από το root του repository: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Το συνοδευτικό `docker-compose.yml` εξυπηρετεί το branch που έχετε κάνει checkout στη διεύθυνση [http://localhost:3377](http://localhost:3377) με live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Μεθοδολογία Pentesting CI/CD**

**Στη HackTricks CI/CD Methodology θα βρείτε πώς να κάνετε pentest σε υποδομές που σχετίζονται με δραστηριότητες CI/CD.** Διαβάστε την ακόλουθη σελίδα για μια **εισαγωγή:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Μεθοδολογία Pentesting Cloud

**Στη HackTricks Cloud Methodology θα βρείτε πώς να κάνετε pentest σε cloud περιβάλλοντα.** Διαβάστε την ακόλουθη σελίδα για μια **εισαγωγή:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Άδεια χρήσης και αποποίηση ευθύνης

**Δείτε τα εδώ:** <sup>[[14]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Στατιστικά Github

![Στατιστικά Github του HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Αναφορές

- [1] [Ο Nacho Piera (@ppieranacho) στο Instagram](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks Cloud training and support banner](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [Το repository HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [Τα branches του HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [Το docker-compose.yml του HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Αναφορά εκτέλεσης container του Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Αναφορά Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [Εντολή mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Τεκμηρίωση του Git clone](https://git-scm.com/docs/git-clone)
- [10] [Τεκμηρίωση του Git checkout](https://git-scm.com/docs/git-checkout)
- [11] [Τεκμηρίωση του Git pull](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Γράφημα στατιστικών Repobeats για το HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
