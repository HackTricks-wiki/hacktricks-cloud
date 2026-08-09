# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos y motion de HackTricks diseñados por_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Ejecutar HackTricks Cloud localmente

El flujo de trabajo a continuación sigue las operaciones documentadas por Git de `clone`, `checkout` y `pull`, así como las ramas de idioma publicadas del repositorio y la configuración del contenedor.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
El comando del contenedor sigue la interfaz `run` documentada de Docker y utiliza el servidor de previsualización HTTP de mdBook; el repositorio asigna el puerto 3000 del contenedor al puerto local 3377.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Tu copia local de HackTricks Cloud estará **disponible en [http://localhost:3377](http://localhost:3377)** después de un minuto.<sup>[[2]](#references)</sup>

Como alternativa, si tienes Docker Compose, ejecuta esto desde la raíz del repositorio:<sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
El archivo `docker-compose.yml` incluido sirve la rama actualmente seleccionada en [http://localhost:3377](http://localhost:3377) con live reload.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Metodología de Pentesting de CI/CD**

**En la HackTricks CI/CD Methodology encontrarás cómo hacer pentesting de la infraestructura relacionada con las actividades de CI/CD.** Lee la siguiente página para obtener una **introducción:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodología de Pentesting de Cloud

**En la HackTricks Cloud Methodology encontrarás cómo hacer pentesting de entornos cloud.** Lee la siguiente página para obtener una **introducción:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licencia y descargo de responsabilidad

**Consúltalos en:**<sup>[[13]](#references)</sup>

[Valores y preguntas frecuentes de HackTricks](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Estadísticas de Github

![Estadísticas de HackTricks Cloud en Github](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## Referencias

- [1] [Nacho Piera (@ppieranacho) en Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Repositorio HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Ramas de HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [docker-compose.yml de HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Referencia para ejecutar contenedores de Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Referencia de Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Referencia del comando mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Documentación de Git clone](https://git-scm.com/docs/git-clone)
- [9] [Documentación de Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Documentación de Git pull](https://git-scm.com/docs/git-pull)
- [11] [Metodología de Pentesting de CI/CD de HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Metodología de Pentesting de Cloud de HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [Valores y preguntas frecuentes de HackTricks](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Gráfico de estadísticas de Repobeats para HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
