# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos und Animationen von HackTricks gestaltet von_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### HackTricks Cloud lokal ausführen

Der folgende Workflow folgt den dokumentierten `clone`-, `checkout`- und `pull`-Operationen von Git sowie den veröffentlichten Sprach-Branches und dem Container-Setup des Repositorys. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Der Container-Befehl folgt der dokumentierten Docker-`run`-Schnittstelle und verwendet den HTTP-Preview-Server von mdBook; das Repository ordnet den Port 3000 des Containers dem lokalen Port 3377 zu. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Ihre lokale Kopie von HackTricks Cloud ist nach einer Minute unter **[http://localhost:3377](http://localhost:3377)** verfügbar. <sup>[[3]](#references)</sup>

Alternativ können Sie diesen Befehl aus dem Repository-Stammverzeichnis ausführen, wenn Sie Docker Compose verwenden: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Die enthaltene `docker-compose.yml` stellt deinen aktuell ausgecheckten Branch unter [http://localhost:3377](http://localhost:3377) mit live reload bereit. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Pentesting-CI/CD-Methodik**

**In der HackTricks-CI/CD-Methodik findest du Informationen dazu, wie du Infrastrukturen im Zusammenhang mit CI/CD-Aktivitäten pentestest.** Lies die folgende Seite für eine **Einführung:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting-Cloud-Methodik

**In der HackTricks-Cloud-Methodik findest du Informationen dazu, wie du Cloud-Umgebungen pentestest.** Lies die folgende Seite für eine **Einführung:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lizenz & Haftungsausschluss

**Siehe sie hier:** <sup>[[14]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub-Statistiken

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Referenzen

- [1] [Nacho Piera (@ppieranacho) auf Instagram](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks Cloud training and support banner](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [HackTricks-wiki/hacktricks-cloud repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [HackTricks Cloud branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Docker container run reference](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Docker Compose up reference](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [mdBook serve command](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Git clone documentation](https://git-scm.com/docs/git-clone)
- [10] [Git checkout documentation](https://git-scm.com/docs/git-checkout)
- [11] [Git pull documentation](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Repobeats statistics graphic for HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
