# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logotypy i animacje HackTricks zaprojektowane przez_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Uruchom HackTricks Cloud lokalnie

Poniższy workflow korzysta z udokumentowanych przez Git operacji `clone`, `checkout` i `pull`, a także z opublikowanych przez repozytorium gałęzi językowych i konfiguracji kontenera.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
Polecenie kontenera jest zgodne z udokumentowanym interfejsem `run` platformy Docker i korzysta z serwera HTTP podglądu mdBook; repozytorium mapuje port 3000 kontenera na lokalny port 3377.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Lokalna kopia HackTricks Cloud będzie **dostępna pod adresem [http://localhost:3377](http://localhost:3377)** po minucie.<sup>[[2]](#references)</sup>

Alternatywnie, jeśli masz Docker Compose, uruchom to z katalogu głównego repozytorium:<sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
Dołączony plik `docker-compose.yml` udostępnia aktualnie wybraną gałąź pod adresem [http://localhost:3377](http://localhost:3377) z funkcją live reload.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Metodologia Pentestingu CI/CD**

**W HackTricks CI/CD Methodology znajdziesz informacje o tym, jak przeprowadzać pentesting infrastruktury związanej z działaniami CI/CD.** Przeczytaj poniższą stronę, aby uzyskać **wprowadzenie:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia Pentestingu Cloud

**W HackTricks Cloud Methodology znajdziesz informacje o tym, jak przeprowadzać pentesting środowisk cloud.** Przeczytaj poniższą stronę, aby uzyskać **wprowadzenie:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licencja i wyłączenie odpowiedzialności

**Sprawdź je tutaj:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statystyki GitHub

![Statystyki HackTricks Cloud na GitHubie](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## Odnośniki

- [1] [Nacho Piera (@ppieranacho) na Instagramie](https://www.instagram.com/ppieranacho/)
- [2] [Repozytorium HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Gałęzie HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [Plik HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Dokumentacja uruchamiania kontenera Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Dokumentacja polecenia Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Dokumentacja polecenia mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Dokumentacja Git clone](https://git-scm.com/docs/git-clone)
- [9] [Dokumentacja Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Dokumentacja Git pull](https://git-scm.com/docs/git-pull)
- [11] [Metodologia Pentestingu HackTricks CI/CD](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Metodologia Pentestingu HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Grafika statystyk Repobeats dla HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
