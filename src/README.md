# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logoları ve hareket tasarımı_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### HackTricks Cloud'u Yerel Olarak Çalıştırma

Aşağıdaki iş akışı Git'in belgelenmiş `clone`, `checkout` ve `pull` işlemlerini, ayrıca repository'nin yayımlanmış dil branch'lerini ve container kurulumunu izler. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Container command, Docker'ın belgelenmiş `run` arayüzünü kullanır ve mdBook'un HTTP preview server'ını çalıştırır; repository, container'ın 3000 portunu yerel 3377 portuna yönlendirir. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

HackTricks Cloud'un yerel kopyası bir dakika sonra **[http://localhost:3377](http://localhost:3377)** adresinde **kullanılabilir olacaktır**. <sup>[[3]](#references)</sup>

Alternatif olarak Docker Compose kullanıyorsanız bunu repository root dizininden çalıştırın: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Bundled `docker-compose.yml`, şu anda checkout edilmiş branch'inizi [http://localhost:3377](http://localhost:3377) adresinde canlı yenileme ile sunar. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Pentesting CI/CD Metodolojisi**

**HackTricks CI/CD Metodolojisi'nde CI/CD etkinlikleriyle ilgili altyapının nasıl pentest edileceğini bulabilirsiniz.** Bir **giriş** için aşağıdaki sayfayı okuyun: <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Metodolojisi

**HackTricks Cloud Metodolojisi'nde cloud ortamlarının nasıl pentest edileceğini bulabilirsiniz.** Bir **giriş** için aşağıdaki sayfayı okuyun: <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisans ve Sorumluluk Reddi

**Bunları burada inceleyin:** <sup>[[14]](#references)</sup>

[HackTricks Değerleri ve SSS](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub İstatistikleri

![HackTricks Cloud GitHub İstatistikleri](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Referanslar

- [1] [Instagram'da Nacho Piera (@ppieranacho)](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks Cloud eğitim ve destek banner'ı](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [HackTricks-wiki/hacktricks-cloud repository'si](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [HackTricks Cloud branch'leri](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Docker container run referansı](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Docker Compose up referansı](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [mdBook serve komutu](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Git clone dokümantasyonu](https://git-scm.com/docs/git-clone)
- [10] [Git checkout dokümantasyonu](https://git-scm.com/docs/git-checkout)
- [11] [Git pull dokümantasyonu](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD Pentesting Metodolojisi](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud Pentesting Metodolojisi](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks Değerleri ve SSS](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [HackTricks Cloud için Repobeats istatistik grafiği](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
