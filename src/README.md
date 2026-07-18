# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks 로고 및 모션 디자인:_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### 로컬에서 HackTricks Cloud 실행
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
잠시 후 로컬 HackTricks Cloud 사본을 **[http://localhost:3377](http://localhost:3377)**에서 사용할 수 있습니다.

또는 Docker Compose가 있다면 repository root에서 다음을 실행하세요:
```bash
docker compose up
```
번들된 `docker-compose.yml`은 live reload와 함께 현재 checkout된 branch를 [http://localhost:3377](http://localhost:3377)에서 제공합니다.

### **Pentesting CI/CD Methodology**

**HackTricks CI/CD Methodology에서는 CI/CD 활동과 관련된 infrastructure를 pentest하는 방법을 확인할 수 있습니다.** 다음 페이지에서 **소개를** 확인하세요:

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**HackTricks Cloud Methodology에서는 cloud environments를 pentest하는 방법을 확인할 수 있습니다.** 다음 페이지에서 **소개를** 확인하세요:

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License & Disclaimer

**다음에서 확인하세요:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Stats

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
