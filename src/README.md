# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks-logo's en animasie ontwerp deur_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Laat HackTricks Cloud Plaaslik Loop

Die werkvloei hieronder volg Git se gedokumenteerde `clone`-, `checkout`- en `pull`-bewerkings, asook die repository se gepubliseerde taalvertakkings en container-opstelling.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
Die container-opdrag volg Docker se gedokumenteerde `run`-koppelvlak en gebruik mdBook se HTTP-previewbediener; die repository karteer die container se poort 3000 na die plaaslike poort 3377.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Jou plaaslike kopie van HackTricks Cloud sal **beskikbaar wees by [http://localhost:3377](http://localhost:3377)** na ongeveer ’n minuut.<sup>[[2]](#references)</sup>

Alternatiewelik, as jy Docker Compose het, voer dit vanaf die repository-wortel uit:<sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
Die ingeslote `docker-compose.yml` bedien jou tans uitgecheckte branch by [http://localhost:3377](http://localhost:3377) met live reload.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD Methodology**

**In die HackTricks CI/CD Methodology sal jy vind hoe om infrastruktuur wat met CI/CD-aktiwiteite verband hou, te pentest.** Lees die volgende bladsy vir ’n **inleiding:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**In die HackTricks Cloud Methodology sal jy vind hoe om cloud-omgewings te pentest.** Lees die volgende bladsy vir ’n **inleiding:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisensie en Vrywaring

**Sien dit by:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub-statistieke

![HackTricks Cloud GitHub-statistieke](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## Verwysings

- [1] [Nacho Piera (@ppieranacho) op Instagram](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Verwysing vir die uitvoer van Docker-containers](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Verwysing vir Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve-opdrag](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone-dokumentasie](https://git-scm.com/docs/git-clone)
- [9] [Git checkout-dokumentasie](https://git-scm.com/docs/git-checkout)
- [10] [Git pull-dokumentasie](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Repobeats-statistiekgrafiek vir HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
