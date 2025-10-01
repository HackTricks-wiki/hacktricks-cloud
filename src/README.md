# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logoları ve hareket tasarımı [_@ppieranacho_](https://www.instagram.com/ppieranacho/) tarafından yapıldı._

### HackTricks Cloud'u Yerel Olarak Çalıştırma
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud

# Select the language you want to use
export LANG="master" # Leave master for English
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
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Yerel HackTricks Cloud kopyanız bir dakika içinde **[http://localhost:3377](http://localhost:3377)** adresinde kullanıma açılacak.

### **Pentesting CI/CD Metodolojisi**

**HackTricks CI/CD Metodolojisi'nde CI/CD faaliyetleriyle ilgili altyapıyı nasıl pentest edeceğinizi bulacaksınız.** Bir **giriş** için aşağıdaki sayfayı okuyun:

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Metodolojisi

**HackTricks Cloud Metodolojisi'nde cloud ortamlarını nasıl pentest edeceğinizi bulacaksınız.** Bir **giriş** için aşağıdaki sayfayı okuyun:

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisans & Sorumluluk Reddi

**Bunları inceleyin:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github İstatistikleri

![HackTricks Cloud Github İstatistikleri](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
