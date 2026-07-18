# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Nembo na motion za HackTricks zilibuniwa na_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Endesha HackTricks Cloud Kwenye Mashine ya Ndani
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
Nakala yako ya ndani ya HackTricks Cloud itakuwa **inapatikana kwenye [http://localhost:3377](http://localhost:3377)** baada ya dakika moja.

Vinginevyo, ikiwa una Docker Compose, endesha hii kutoka kwenye mzizi wa repository:
```bash
docker compose up
```
### **Pentesting CI/CD Methodology**

**Katika HackTricks CI/CD Methodology utapata jinsi ya kufanya pentest kwenye infrastructure inayohusiana na shughuli za CI/CD.** Soma ukurasa ufuatao kwa **utangulizi:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**Katika HackTricks Cloud Methodology utapata jinsi ya kufanya pentest kwenye cloud environments.** Soma ukurasa ufuatao kwa **utangulizi:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Leseni na Kanusho

**Ziangalie hapa:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Takwimu za HackTricks Cloud kwenye GitHub

![Takwimu za HackTricks Cloud kwenye GitHub](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
