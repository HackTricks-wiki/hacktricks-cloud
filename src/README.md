# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logo et animation de Hacktricks conçus par_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Exécuter HackTricks Cloud Localement
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Votre copie locale de HackTricks Cloud sera **disponible à [http://localhost:3377](http://localhost:3377)** après une minute.

### **Méthodologie de Pentesting CI/CD**

**Dans la méthodologie CI/CD de HackTricks, vous trouverez comment pentester l'infrastructure liée aux activités CI/CD.** Lisez la page suivante pour une **introduction :**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Méthodologie de Pentesting Cloud

**Dans la méthodologie Cloud de HackTricks, vous trouverez comment pentester les environnements cloud.** Lisez la page suivante pour une **introduction :**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licence & Avertissement

**Vérifiez-les dans :**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statistiques Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
