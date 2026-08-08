# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logotipe i animaciju za Hacktricks dizajnirao je_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)._ <sup>[[1]](#references)[[3]](#references)</sup>

### Pokretanje HackTricks Cloud lokalno

Tok rada u nastavku prati Git-ove dokumentovane operacije `clone`, `checkout` i `pull`, kao i objavljene grane jezika i postavku kontejnera u repozitorijumu. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Komanda kontejnera prati Docker-ov dokumentovani interfejs `run` i koristi mdBook-ov HTTP server za pregled; repository mapira port kontejnera 3000 na lokalni port 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Lokalna kopija HackTricks Cloud biće **dostupna na [http://localhost:3377](http://localhost:3377)** nakon jednog minuta. <sup>[[3]](#references)</sup>

Alternativno, ako imate Docker Compose, pokrenite ovo iz root direktorijuma repository-ja: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Bundled `docker-compose.yml` servira trenutno checkout-ovanu granu na adresi [http://localhost:3377](http://localhost:3377) uz live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Pentesting CI/CD metodologija**

**U HackTricks CI/CD metodologiji pronaći ćete kako da obavite pentesting infrastrukture povezane sa CI/CD aktivnostima.** Pročitajte sledeću stranicu za **uvod:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud metodologija

**U HackTricks Cloud metodologiji pronaći ćete kako da obavite pentesting cloud okruženja.** Pročitajte sledeću stranicu za **uvod:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licenca i odricanje odgovornosti

**Pogledajte ih ovde:** <sup>[[14]](#references)</sup>

[HackTricks vrednosti i FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github statistika

![HackTricks Cloud Github statistika](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Reference

- [1] [Nacho Piera (@ppieranacho) na Instagramu](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks Cloud banner za obuku i podršku](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [HackTricks-wiki/hacktricks-cloud repozitorijum](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [HackTricks Cloud grane](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Referenca za pokretanje Docker containera](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Referenca za Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [Referenca za komandu mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Git clone dokumentacija](https://git-scm.com/docs/git-clone)
- [10] [Git checkout dokumentacija](https://git-scm.com/docs/git-checkout)
- [11] [Git pull dokumentacija](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD Pentesting metodologija](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud Pentesting metodologija](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks vrednosti i FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Repobeats grafikon statistike za HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
