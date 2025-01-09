# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_I loghi e il design in movimento di Hacktricks sono stati creati da_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Esegui HackTricks Cloud Localmente
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
La tua copia locale di HackTricks Cloud sarà **disponibile su [http://localhost:3377](http://localhost:3377)** dopo un minuto.

### **Metodologia di Pentesting CI/CD**

**Nella Metodologia CI/CD di HackTricks troverai come effettuare pentesting su infrastrutture relative ad attività CI/CD.** Leggi la pagina seguente per un'**introduzione:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia di Pentesting Cloud

**Nella Metodologia Cloud di HackTricks troverai come effettuare pentesting su ambienti cloud.** Leggi la pagina seguente per un'**introduzione:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licenza e Dichiarazione di Non Responsabilità

**Controllali in:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statistiche di Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
