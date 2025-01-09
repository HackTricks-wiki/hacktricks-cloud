# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Loga Hacktricks i animacja zaprojektowane przez_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Uruchom HackTricks Cloud lokalnie
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Twoja lokalna kopia HackTricks Cloud będzie **dostępna pod adresem [http://localhost:3377](http://localhost:3377)** po minucie.

### **Metodologia Pentestingu CI/CD**

**W Metodologii CI/CD HackTricks znajdziesz, jak przeprowadzać pentesting infrastruktury związanej z działaniami CI/CD.** Przeczytaj następującą stronę, aby uzyskać **wprowadzenie:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia Pentestingu w Chmurze

**W Metodologii Chmury HackTricks znajdziesz, jak przeprowadzać pentesting środowisk chmurowych.** Przeczytaj następującą stronę, aby uzyskać **wprowadzenie:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licencja i Zastrzeżenie

**Sprawdź je w:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Statystyki Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
