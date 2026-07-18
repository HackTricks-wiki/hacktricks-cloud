# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Loghi e motion design di_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Esegui HackTricks Cloud localmente
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
La tua copia locale di HackTricks Cloud sarà **disponibile all'indirizzo [http://localhost:3377](http://localhost:3377)** dopo un minuto.

In alternativa, se disponi di Docker Compose, esegui questo comando dalla root del repository:
```bash
docker compose up
```
Il file `docker-compose.yml` incluso serve il branch attualmente selezionato su [http://localhost:3377](http://localhost:3377) con live reload.

### **Pentesting CI/CD Methodology**

**Nella HackTricks CI/CD Methodology troverai come eseguire il pentesting dell'infrastruttura correlata alle attività CI/CD.** Leggi la pagina seguente per un'**introduzione:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**Nella HackTricks Cloud Methodology troverai come eseguire il pentesting degli ambienti cloud.** Leggi la pagina seguente per un'**introduzione:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licenza e disclaimer

**Consultali qui:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statistiche Github

![Statistiche Github di HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
