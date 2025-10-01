# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks 로고 및 모션 디자인:_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### 로컬에서 HackTricks Cloud 실행
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud

# Select the language you want to use
export LANG="master" # Leave master for English
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
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
로컬에 복제된 HackTricks Cloud는 **[http://localhost:3377](http://localhost:3377)**에서 1분 후 이용할 수 있습니다.

### **Pentesting CI/CD 방법론**

**In the HackTricks CI/CD Methodology you will find how to pentest infrastructure related to CI/CD activities.** 다음 페이지에서 **소개:**를 읽으세요:

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud 방법론

**In the HackTricks Cloud Methodology you will find how to pentest cloud environments.** 다음 페이지에서 **소개:**를 읽으세요:

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### 라이선스 & 고지사항

**다음에서 확인하세요:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github 통계

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
