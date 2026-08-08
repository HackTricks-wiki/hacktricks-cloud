# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Loghi e animazioni di Hacktricks progettati da_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### Eseguire HackTricks Cloud localmente

Il workflow seguente segue le operazioni documentate da Git `clone`, `checkout` e `pull`, nonché i branch linguistici pubblicati del repository e la configurazione dei container. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Il comando del container segue l'interfaccia `run` documentata da Docker e utilizza il server di anteprima HTTP di mdBook; il repository associa la porta 3000 del container alla porta locale 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

La tua copia locale di HackTricks Cloud sarà **disponibile all'indirizzo [http://localhost:3377](http://localhost:3377)** dopo un minuto. <sup>[[3]](#references)</sup>

In alternativa, se disponi di Docker Compose, esegui questo comando dalla radice del repository: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Il file `docker-compose.yml` incluso serve il branch attualmente sottoposto a checkout su [http://localhost:3377](http://localhost:3377) con live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Metodologia di Pentesting CI/CD**

**Nella HackTricks CI/CD Methodology troverai come eseguire il pentesting dell'infrastruttura relativa alle attività CI/CD.** Leggi la pagina seguente per un'**introduzione:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia di Pentesting Cloud

**Nella HackTricks Cloud Methodology troverai come eseguire il pentesting degli ambienti cloud.** Leggi la pagina seguente per un'**introduzione:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licenza e Disclaimer

**Consultali qui:** <sup>[[14]](#references)</sup>

[Valori e FAQ di HackTricks](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statistiche GitHub

![Statistiche GitHub di HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Riferimenti

- [1] [Nacho Piera (@ppieranacho) su Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Banner per la formazione e il supporto di HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [Repository HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [Branch di HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [docker-compose.yml di HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Riferimento per l'esecuzione dei container Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Riferimento per Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [Riferimento per il comando mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Documentazione di Git clone](https://git-scm.com/docs/git-clone)
- [10] [Documentazione di Git checkout](https://git-scm.com/docs/git-checkout)
- [11] [Documentazione di Git pull](https://git-scm.com/docs/git-pull)
- [12] [Metodologia di Pentesting CI/CD di HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [Metodologia di Pentesting Cloud di HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [Valori e FAQ di HackTricks](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Grafico delle statistiche Repobeats per HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
