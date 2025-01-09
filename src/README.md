# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logotipi i animacije dizajnirao_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Pokrenite HackTricks Cloud lokalno
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Vaša lokalna kopija HackTricks Cloud biće **dostupna na [http://localhost:3377](http://localhost:3377)** nakon minuta.

### **Pentesting CI/CD Metodologija**

**U HackTricks CI/CD Metodologiji ćete pronaći kako da pentestirate infrastrukturu vezanu za CI/CD aktivnosti.** Pročitajte sledeću stranicu za **uvod:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Metodologija

**U HackTricks Cloud Metodologiji ćete pronaći kako da pentestirate cloud okruženja.** Pročitajte sledeću stranicu za **uvod:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licenca & Odricanje

**Proverite ih u:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Statistika

![HackTricks Cloud Github Statistika](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
