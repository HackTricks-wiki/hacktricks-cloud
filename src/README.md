# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logos & motion designed by_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Endesha HackTricks Cloud Kwenye Kompyuta Yako
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Nakala yako ya ndani ya HackTricks Cloud itapatikana **katika [http://localhost:3377](http://localhost:3377)** baada ya dakika moja.

### **Mbinu za Pentesting CI/CD**

**Katika Mbinu za CI/CD za HackTricks utaona jinsi ya pentest miundombinu inayohusiana na shughuli za CI/CD.** Soma ukurasa ufuatao kwa **utangulizi:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Mbinu za Pentesting Cloud

**Katika Mbinu za Cloud za HackTricks utaona jinsi ya pentest mazingira ya wingu.** Soma ukurasa ufuatao kwa **utangulizi:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Leseni & Kanusho

**Angalia katika:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Takwimu za Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
