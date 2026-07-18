# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks-logo's en animasie ontwerp deur_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Begin HackTricks Cloud plaaslik loods
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
Jou plaaslike kopie van HackTricks Cloud sal **beskikbaar wees by [http://localhost:3377](http://localhost:3377)** ná ’n minuut.

Alternatiewelik, as jy Docker Compose het, voer die volgende vanaf die wortel van die repository uit:
```bash
docker compose up
```
Die ingeslote `docker-compose.yml` bedien jou tans uitgeklokte branch by [http://localhost:3377](http://localhost:3377) met live reload.

### **Pentesting CI/CD-metodologie**

**In die HackTricks CI/CD-metodologie sal jy leer hoe om infrastruktuur wat met CI/CD-aktiwiteite verband hou, te pentest.** Lees die volgende bladsy vir ’n **inleiding:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud-metodologie

**In die HackTricks Cloud-metodologie sal jy leer hoe om cloud-omgewings te pentest.** Lees die volgende bladsy vir ’n **inleiding:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisensie en vrywaring

**Gaan dit na by:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github-statistieke

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
