# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_HackTricks-logo's en animasie ontwerp deur_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### Begin HackTricks Cloud plaaslik

Die werkvloei hieronder volg Git se gedokumenteerde `clone`-, `checkout`- en `pull`-bewerkings, asook die repository se gepubliseerde taalbranches en container-opstelling. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Die container-opdrag volg Docker se gedokumenteerde `run`-interface en gebruik mdBook se HTTP-voorskoubediende; die repository karteer die container se poort 3000 na plaaslike poort 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Jou plaaslike kopie van HackTricks Cloud sal **beskikbaar wees by [http://localhost:3377](http://localhost:3377)** ná ’n minuut. <sup>[[3]](#references)</sup>

Alternatiewelik, indien jy Docker Compose het, voer die volgende vanaf die repository-wortel uit: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Die gebundelde `docker-compose.yml` bedien jou tans checked-out branch by [http://localhost:3377](http://localhost:3377) met live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Pentesting CI/CD-metodologie**

**In die HackTricks CI/CD-metodologie sal jy vind hoe om infrastruktuur wat met CI/CD-aktiwiteite verband hou, te pentest.** Lees die volgende bladsy vir ’n **inleiding:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud-metodologie

**In die HackTricks Cloud-metodologie sal jy vind hoe om cloud-omgewings te pentest.** Lees die volgende bladsy vir ’n **inleiding:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Lisensie & Vrywaring

**Bekyk dit by:** <sup>[[14]](#references)</sup>

[HackTricks-waardes & Gereelde vrae](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub-statistieke

![HackTricks Cloud GitHub-statistieke](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Verwysings

- [1] [Nacho Piera (@ppieranacho) op Instagram](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks Cloud training- en ondersteuningsbanier](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [HackTricks-wiki/hacktricks-cloud-bewaarplek](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [HackTricks Cloud-branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Verwysing vir die uitvoer van Docker-houers](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Verwysing vir Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [mdBook serve-opdrag](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Git clone-dokumentasie](https://git-scm.com/docs/git-clone)
- [10] [Git checkout-dokumentasie](https://git-scm.com/docs/git-checkout)
- [11] [Git pull-dokumentasie](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD-pentestingmetodologie](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud-pentestingmetodologie](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks-waardes & Gereelde vrae](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Repobeats-statistiekgrafiek vir HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
