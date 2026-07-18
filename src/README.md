# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logoları ve hareket tasarımı_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_ tarafından yapılmıştır._

### HackTricks Cloud'u Yerel Olarak Çalıştır
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
HackTricks Cloud'un yerel kopyası bir dakika sonra **[http://localhost:3377](http://localhost:3377)** adresinde kullanılabilir olacaktır.

Alternatif olarak, Docker Compose kullanıyorsanız bunu repository root dizininden çalıştırın:
```bash
docker compose up
```
Bundled `docker-compose.yml`, canlı yeniden yükleme ile şu anda checkout edilmiş branch'inizi [http://localhost:3377](http://localhost:3377) adresinde sunar.

### **Pentesting CI/CD Methodology**

**HackTricks CI/CD Methodology içinde CI/CD etkinlikleriyle ilgili altyapının nasıl pentest edileceğini bulabilirsiniz.** Bir **giriş** için aşağıdaki sayfayı okuyun:

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**HackTricks Cloud Methodology içinde cloud ortamlarının nasıl pentest edileceğini bulabilirsiniz.** Bir **giriş** için aşağıdaki sayfayı okuyun:

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisans ve Sorumluluk Reddi

**Bunları burada inceleyin:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github İstatistikleri

![HackTricks Cloud Github İstatistikleri](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
