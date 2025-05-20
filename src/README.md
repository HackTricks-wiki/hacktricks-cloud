# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks-Logos & Motion von_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_ entworfen._

### Führen Sie HackTricks Cloud lokal aus
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
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git checkout $LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Ihre lokale Kopie von HackTricks Cloud wird **unter [http://localhost:3377](http://localhost:3377)** nach einer Minute **verfügbar sein.**

### **Pentesting CI/CD Methodologie**

**In der HackTricks CI/CD Methodologie finden Sie, wie man Infrastruktur im Zusammenhang mit CI/CD-Aktivitäten pentestet.** Lesen Sie die folgende Seite für eine **Einführung:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodologie

**In der HackTricks Cloud Methodologie finden Sie, wie man Cloud-Umgebungen pentestet.** Lesen Sie die folgende Seite für eine **Einführung:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lizenz & Haftungsausschluss

**Überprüfen Sie sie in:**

[HackTricks Werte & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Statistiken

![HackTricks Cloud Github Statistiken](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
