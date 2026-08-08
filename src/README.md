# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logo za Hacktricks na motion vimeundwa na_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)</sup>

### Endesha HackTricks Cloud Kwenye Kompyuta Yako

Mchakato ulio hapa chini unafuata operesheni za `clone`, `checkout`, na `pull` zilizoandikwa katika nyaraka za Git, pamoja na branches za lugha zilizochapishwa za repository na usanidi wa container. <sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
The container command inafuata interface ya Docker iliyowekwa kwenye nyaraka ya `run` na inatumia HTTP preview server ya mdBook; repository inaunganisha port 3000 ya container na port 3377 ya ndani. <sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Nakala yako ya ndani ya HackTricks Cloud **itapatikana kwenye [http://localhost:3377](http://localhost:3377)** baada ya dakika moja. <sup>[[2]](#references)</sup>

Vinginevyo, ikiwa una Docker Compose, endesha hii kutoka kwenye mzizi wa repository: <sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
Faili ya `docker-compose.yml` iliyojumuishwa inahudumia branch yako iliyokaguliwa kwa sasa kwenye [http://localhost:3377](http://localhost:3377), ikiwa na live reload. <sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD Methodology**

**Katika HackTricks CI/CD Methodology utapata jinsi ya kupentest miundombinu inayohusiana na shughuli za CI/CD.** Soma ukurasa ufuatao kwa **utangulizi:** <sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**Katika HackTricks Cloud Methodology utapata jinsi ya kupentest mazingira ya cloud.** Soma ukurasa ufuatao kwa **utangulizi:** <sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Leseni na Kanusho

**Zipate hapa:** <sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Takwimu za Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[14]](#references)</sup>

## Marejeleo

- [1] [Nacho Piera (@ppieranacho) kwenye Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Hazina ya HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Branches za HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Marejeleo ya kuendesha Docker container](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Marejeleo ya Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Amri ya mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Nyaraka za Git clone](https://git-scm.com/docs/git-clone)
- [9] [Nyaraka za Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Nyaraka za Git pull](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Mchoro wa takwimu za Repobeats wa HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
