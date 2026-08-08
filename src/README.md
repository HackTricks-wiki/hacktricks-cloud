# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logo na motion za Hacktricks zilibuniwa na_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### Endesha HackTricks Cloud Kwenye Kompyuta Yako

Mtiririko wa kazi hapa chini unafuata operesheni za `clone`, `checkout`, na `pull` zilizowekwa kwenye nyaraka za Git, pamoja na language branches zilizochapishwa na container setup ya repository. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Amri ya container hufuata interface ya `run` iliyoandikwa na Docker na hutumia HTTP preview server ya mdBook; repository huunganisha port 3000 ya container na port ya ndani 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Nakili yako ya ndani ya HackTricks Cloud **itapatikana kwenye [http://localhost:3377](http://localhost:3377)** baada ya dakika moja. <sup>[[3]](#references)</sup>

Vinginevyo, ikiwa una Docker Compose, endesha hii kutoka kwenye mzizi wa repository: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Bundled `docker-compose.yml` huhudumia branch yako iliyo-checkout kwa sasa kwenye [http://localhost:3377](http://localhost:3377) ikiwa na live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Methodology ya Pentesting CI/CD**

**Katika HackTricks CI/CD Methodology utapata jinsi ya kufanya pentest ya infrastructure inayohusiana na shughuli za CI/CD.** Soma ukurasa ufuatao kwa ajili ya **utangulizi:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Methodology ya Pentesting Cloud

**Katika HackTricks Cloud Methodology utapata jinsi ya kufanya pentest ya cloud environments.** Soma ukurasa ufuatao kwa ajili ya **utangulizi:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Leseni na Kanusho

**Ziangalie hapa:** <sup>[[14]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Takwimu za Github

![Takwimu za HackTricks Cloud Github](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Marejeo

- [1] [Nacho Piera (@ppieranacho) kwenye Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Bango la mafunzo na support la HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [Repository ya HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [Branches za HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [docker-compose.yml ya HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Marejeo ya kuendesha Docker container](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Marejeo ya Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [Amri ya mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Nyaraka za Git clone](https://git-scm.com/docs/git-clone)
- [10] [Nyaraka za Git checkout](https://git-scm.com/docs/git-checkout)
- [11] [Nyaraka za Git pull](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Mchoro wa takwimu za Repobeats kwa HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
