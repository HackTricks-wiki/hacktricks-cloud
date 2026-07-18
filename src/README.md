# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos et animation de HackTricks conçus par_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Exécuter HackTricks Cloud localement
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
Votre copie locale de HackTricks Cloud sera **disponible à l'adresse [http://localhost:3377](http://localhost:3377)** après une minute.

Sinon, si vous disposez de Docker Compose, exécutez ceci depuis la racine du dépôt :
```bash
docker compose up
```
Le fichier `docker-compose.yml` fourni sert votre branche actuellement extraite à l’adresse [http://localhost:3377](http://localhost:3377) avec rechargement en direct.

### **Méthodologie de pentesting CI/CD**

**Dans la HackTricks CI/CD Methodology, vous trouverez comment effectuer le pentesting d’infrastructures liées aux activités CI/CD.** Consultez la page suivante pour une **introduction :**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Méthodologie de pentesting Cloud

**Dans la HackTricks Cloud Methodology, vous trouverez comment effectuer le pentesting d’environnements Cloud.** Consultez la page suivante pour une **introduction :**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licence et avertissement

**Consultez-les ici :**

[Valeurs et FAQ de HackTricks](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statistiques Github

![Statistiques Github de HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
