# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos y movimiento de HackTricks diseñados por_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Ejecuta HackTricks Cloud localmente
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
Tu copia local de HackTricks Cloud estará **disponible en [http://localhost:3377](http://localhost:3377)** después de un minuto.

Como alternativa, si tienes Docker Compose, ejecuta esto desde la raíz del repositorio:
```bash
docker compose up
```
El `docker-compose.yml` incluido sirve tu branch actualmente seleccionado en [http://localhost:3377](http://localhost:3377) con recarga en vivo.

### **Metodología de Pentesting CI/CD**

**En la Metodología de CI/CD de HackTricks encontrarás cómo hacer pentesting de la infraestructura relacionada con actividades de CI/CD.** Lee la siguiente página para una **introducción:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodología de Pentesting Cloud

**En la Metodología Cloud de HackTricks encontrarás cómo hacer pentesting de entornos cloud.** Lee la siguiente página para una **introducción:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licencia y descargo de responsabilidad

**Consúltalos en:**

[Valores y preguntas frecuentes de HackTricks](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Estadísticas de Github

![Estadísticas de Github Cloud de HackTricks](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
