# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logoları ve animasyonu_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_ tarafından tasarlanmıştır._<sup>[[1]](#references)</sup>

### HackTricks Cloud'u Yerel Olarak Çalıştırma

Aşağıdaki iş akışı, Git'in belgelenmiş `clone`, `checkout` ve `pull` işlemlerini ve deponun yayımlanmış dil dalları ile container kurulumunu izler.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

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
# "vi" for Vietnamese
# "zh" for Chinese

# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $HT_LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```

Konteyner komutu, Docker'ın belgelenmiş `run` arayüzünü kullanır ve mdBook'un HTTP önizleme sunucusunu çalıştırır; repository, konteynerin 3000 numaralı portunu yerel 3377 numaralı porta eşler.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Bir dakika sonra HackTricks Cloud'un yerel kopyasına **[http://localhost:3377](http://localhost:3377)** adresinden erişebilirsiniz.<sup>[[2]](#references)</sup>

Alternatif olarak, Docker Compose kullanıyorsanız repository'nin kök dizininde şu komutu çalıştırın:<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

Birlikte gelen `docker-compose.yml`, checkout edilmiş mevcut branch’inizi canlı yeniden yükleme ile [http://localhost:3377](http://localhost:3377) adresinde sunar.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD Metodolojisi**

**HackTricks CI/CD Metodolojisi’nde, CI/CD etkinlikleriyle ilgili altyapının nasıl pentest edileceğini bulabilirsiniz.** Bir **giriş** için aşağıdaki sayfayı okuyun:<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Cloud Pentesting Metodolojisi

**HackTricks Cloud Metodolojisi’nde, cloud ortamlarının nasıl pentest edileceğini bulabilirsiniz.** Bir **giriş** için aşağıdaki sayfayı okuyun:<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisans ve Sorumluluk Reddi

**Şunları inceleyin:**<sup>[[13]](#references)</sup>

[HackTricks Değerleri ve SSS](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub İstatistikleri

![HackTricks Cloud GitHub İstatistikleri](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## References

- [1] [Nacho Piera (@ppieranacho) Instagram'da](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud deposu](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud branch’leri](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Docker container çalıştırma referansı](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Docker Compose up referansı](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve komutu](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone belgeleri](https://git-scm.com/docs/git-clone)
- [9] [Git checkout belgeleri](https://git-scm.com/docs/git-checkout)
- [10] [Git pull belgeleri](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting Metodolojisi](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting Metodolojisi](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Değerleri ve SSS](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [HackTricks Cloud için Repobeats istatistik grafiği](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)
{{#include ./banners/hacktricks-training.md}}
