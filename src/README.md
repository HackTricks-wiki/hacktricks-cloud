# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logoları ve hareket tasarımı_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_ tarafından yapılmıştır._

### HackTricks Cloud'u Yerel Olarak Çalıştırın
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Yerel kopyanız HackTricks Cloud **bir dakika sonra [http://localhost:3377](http://localhost:3377)** adresinde **mevcut olacak.**

### **Pentesting CI/CD Metodolojisi**

**HackTricks CI/CD Metodolojisinde, CI/CD faaliyetleri ile ilgili altyapıyı nasıl pentest edeceğinizi bulacaksınız.** Aşağıdaki sayfayı bir **giriş için** okuyun:

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Metodolojisi

**HackTricks Cloud Metodolojisinde, bulut ortamlarını nasıl pentest edeceğinizi bulacaksınız.** Aşağıdaki sayfayı bir **giriş için** okuyun:

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisans & Feragatname

**Onları kontrol edin:**

[HackTricks Değerleri & SSS](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github İstatistikleri

![HackTricks Cloud Github İstatistikleri](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
