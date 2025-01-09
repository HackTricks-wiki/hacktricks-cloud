# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logo's & bewegingsontwerp deur_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Voer HackTricks Cloud Plaaslik Uit
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Jou plaaslike kopie van HackTricks Cloud sal **beskikbaar wees by [http://localhost:3377](http://localhost:3377)** na 'n minuut.

### **Pentesting CI/CD Metodologie**

**In die HackTricks CI/CD Metodologie sal jy vind hoe om infrastruktuur wat verband hou met CI/CD aktiwiteite te pentest.** Lees die volgende bladsy vir 'n **inleiding:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Metodologie

**In die HackTricks Cloud Metodologie sal jy vind hoe om wolkomgewings te pentest.** Lees die volgende bladsy vir 'n **inleiding:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisensie & Vrywaring

**Kyk hulle in:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Statistieke

![HackTricks Cloud Github Statistieke](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
