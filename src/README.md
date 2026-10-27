# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos et animation HackTricks conçus par_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Exécuter HackTricks Cloud localement

Le flux de travail ci-dessous suit les opérations `clone`, `checkout` et `pull` documentées par Git, ainsi que les branches linguistiques publiées du dépôt et sa configuration de conteneur.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

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
# "vi" for Vietnamese
# "zh" for Chinese

# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $HT_LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```

La commande du conteneur suit l’interface `run` documentée par Docker et utilise le serveur d’aperçu HTTP de mdBook ; le dépôt associe le port 3000 du conteneur au port local 3377.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Votre copie locale de HackTricks Cloud sera **disponible à [http://localhost:3377](http://localhost:3377)** après une minute.<sup>[[2]](#references)</sup>

Vous pouvez également, si vous disposez de Docker Compose, lancer cette commande depuis la racine du dépôt :<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

Le fichier `docker-compose.yml` fourni sert la branche actuellement extraite à [http://localhost:3377](http://localhost:3377) avec rechargement à chaud.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Méthodologie de pentesting CI/CD**

**Dans la méthodologie CI/CD de HackTricks, vous découvrirez comment effectuer des pentests sur les infrastructures liées aux activités CI/CD.** Consultez la page suivante pour une **introduction :**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Méthodologie de pentesting Cloud

**Dans la méthodologie Cloud de HackTricks, vous découvrirez comment effectuer des pentests sur les environnements cloud.** Consultez la page suivante pour une **introduction :**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licence et avis de non-responsabilité

**Consultez-les ici :**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statistiques GitHub

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## References

- [1] [Nacho Piera (@ppieranacho) sur Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Dépôt HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Branches HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [Fichier docker-compose.yml de HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Référence d’exécution d’un conteneur Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Référence de la commande Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Commande mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Documentation de git clone](https://git-scm.com/docs/git-clone)
- [9] [Documentation de git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Documentation de git pull](https://git-scm.com/docs/git-pull)
- [11] [Méthodologie de pentesting CI/CD de HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Méthodologie de pentesting Cloud de HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Graphique des statistiques Repobeats pour HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)
{{#include ./banners/hacktricks-training.md}}
