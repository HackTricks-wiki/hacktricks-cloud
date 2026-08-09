# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks-Logos und -Animationen entworfen von_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### HackTricks Cloud lokal ausführen

Der folgende Workflow folgt den von Git dokumentierten Vorgängen `clone`, `checkout` und `pull` sowie den veröffentlichten Sprach-Branches und dem Container-Setup des Repositorys.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
Der Container-Befehl folgt der dokumentierten `run`-Schnittstelle von Docker und verwendet den HTTP-Vorschauserver von mdBook; das Repository ordnet den Container-Port 3000 dem lokalen Port 3377 zu.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Ihre lokale Kopie von HackTricks Cloud ist nach einer Minute **unter [http://localhost:3377](http://localhost:3377) verfügbar**.<sup>[[2]](#references)</sup>

Alternativ können Sie diesen Befehl aus dem Stammverzeichnis des Repositorys ausführen, wenn Sie Docker Compose haben:<sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
Die gebundelte `docker-compose.yml` stellt deinen aktuell ausgecheckten Branch unter [http://localhost:3377](http://localhost:3377) mit live reload bereit.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting-CI/CD-Methodik**

**In der HackTricks CI/CD-Methodik erfährst du, wie du Infrastruktur im Zusammenhang mit CI/CD-Aktivitäten pentestest.** Lies die folgende Seite als **Einführung:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting-Cloud-Methodik

**In der HackTricks Cloud-Methodik erfährst du, wie du Cloud-Umgebungen pentestest.** Lies die folgende Seite als **Einführung:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lizenz & Haftungsausschluss

**Siehe:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub-Statistiken

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## Referenzen

- [1] [Nacho Piera (@ppieranacho) auf Instagram](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud-Repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks-Cloud-Branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Referenz zum Ausführen von Docker-Containern](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Referenz zu Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Referenz zum mdBook-serve-Befehl](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Dokumentation zu Git clone](https://git-scm.com/docs/git-clone)
- [9] [Dokumentation zu Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Dokumentation zu Git pull](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting-Methodik](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting-Methodik](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Repobeats-Statistikgrafik für HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
