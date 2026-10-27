# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Alama za biashara na miondoko ya Hacktricks zimeundwa na_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Endesha HackTricks Cloud Kwenye Mazingira ya Ndani

Mtiririko wa kazi ulio hapa chini unafuata utaratibu wa Git ulioandikwa wa `clone`, `checkout`, na `pull`, pamoja na matawi ya lugha yaliyochapishwa ya repository na usanidi wa container.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

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

Amri ya container inafuata kiolesura cha `run` kilichoandikwa kwenye nyaraka za Docker na hutumia seva ya onyesho la kukagua ya HTTP ya mdBook; repository inaelekeza port 3000 ya container kwenye port 3377 ya kompyuta yako.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Nakili yako ya ndani ya HackTricks Cloud **itapatikana kwenye [http://localhost:3377](http://localhost:3377)** baada ya dakika moja.<sup>[[2]](#references)</sup>

Vinginevyo, ikiwa una Docker Compose, endesha hili kutoka kwenye mzizi wa repository:<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

`docker-compose.yml` iliyojumuishwa inaonyesha branch uliyo-checkout kwa sasa kwenye [http://localhost:3377](http://localhost:3377), ikiwa na live reload.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Mbinu ya Pentesting CI/CD**

**Katika Mbinu ya CI/CD ya HackTricks utapata maelezo ya jinsi ya kufanya pentest kwenye miundombinu inayohusiana na shughuli za CI/CD.** Soma ukurasa ufuatao kwa **utangulizi:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Mbinu ya Pentesting Cloud

**Katika Mbinu ya Cloud ya HackTricks utapata maelezo ya jinsi ya kufanya pentest kwenye mazingira ya cloud.** Soma ukurasa ufuatao kwa **utangulizi:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Leseni na Kanusho

**Zipitie hapa:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Takwimu za Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## References

- [1] [Nacho Piera (@ppieranacho) kwenye Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Repository ya HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Branch za HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [docker-compose.yml ya HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Marejeleo ya kuendesha Docker container](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Marejeleo ya Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Amri ya mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Nyaraka za Git clone](https://git-scm.com/docs/git-clone)
- [9] [Nyaraka za Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Nyaraka za Git pull](https://git-scm.com/docs/git-pull)
- [11] [Mbinu ya Pentesting CI/CD ya HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Mbinu ya Pentesting Cloud ya HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Mchoro wa takwimu za Repobeats kwa HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)
{{#include ./banners/hacktricks-training.md}}
