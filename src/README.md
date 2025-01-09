# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Los logotipos y el diseño en movimiento de Hacktricks son de_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Ejecutar HackTricks Cloud Localmente
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Tu copia local de HackTricks Cloud estará **disponible en [http://localhost:3377](http://localhost:3377)** después de un minuto.

### **Metodología de Pentesting CI/CD**

**En la Metodología de CI/CD de HackTricks encontrarás cómo realizar pentesting en infraestructuras relacionadas con actividades de CI/CD.** Lee la siguiente página para una **introducción:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodología de Pentesting en la Nube

**En la Metodología de la Nube de HackTricks encontrarás cómo realizar pentesting en entornos de nube.** Lee la siguiente página para una **introducción:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licencia y Descargo de Responsabilidad

**Consúltalos en:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Estadísticas de Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
