# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_ Hacktricks-Logos und Animation gestaltet von_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### HackTricks Cloud lokal ausführen
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
Ihre lokale Kopie von HackTricks Cloud ist nach einer Minute unter [http://localhost:3377](http://localhost:3377) **verfügbar**.

Alternativ können Sie, wenn Sie Docker Compose haben, Folgendes aus dem Stammverzeichnis des Repositorys ausführen:
```bash
docker compose up
```
Die gebündelte `docker-compose.yml` stellt deinen aktuell ausgecheckten Branch unter [http://localhost:3377](http://localhost:3377) mit live reload bereit.

### **Pentesting CI/CD Methodology**

**In der HackTricks CI/CD Methodology findest du Informationen darüber, wie du Infrastruktur im Zusammenhang mit CI/CD-Aktivitäten pentesten kannst.** Lies die folgende Seite als **Einführung:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**In der HackTricks Cloud Methodology findest du Informationen darüber, wie du Cloud-Umgebungen pentesten kannst.** Lies die folgende Seite als **Einführung:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lizenz & Haftungsausschluss

**Hier findest du sie:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub-Statistiken

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
