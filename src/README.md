# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks 로고 및 모션 디자인:_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)</sup>

### HackTricks Cloud를 로컬에서 실행

아래 워크플로는 Git에 문서화된 `clone`, `checkout`, `pull` 작업과 repository에서 공개된 언어별 branch 및 container 설정을 따릅니다. <sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
컨테이너 명령은 Docker의 문서화된 `run` 인터페이스를 따르며 mdBook의 HTTP preview server를 사용합니다. 저장소는 컨테이너의 포트 3000을 로컬 포트 3377에 매핑합니다. <sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

잠시 후 로컬 HackTricks Cloud 사본을 **[http://localhost:3377](http://localhost:3377)**에서 사용할 수 있습니다. <sup>[[2]](#references)</sup>

또는 Docker Compose가 있는 경우 저장소 루트에서 다음을 실행합니다. <sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
포함된 `docker-compose.yml`은 현재 checkout된 branch를 live reload와 함께 [http://localhost:3377](http://localhost:3377)에서 제공합니다. <sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **CI/CD Pentesting Methodology**

**HackTricks CI/CD Methodology에서는 CI/CD 활동과 관련된 인프라를 pentest하는 방법을 확인할 수 있습니다.** 다음 페이지에서 **소개:**를 읽어보세요. <sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Cloud Pentesting Methodology

**HackTricks Cloud Methodology에서는 cloud 환경을 pentest하는 방법을 확인할 수 있습니다.** 다음 페이지에서 **소개:**를 읽어보세요. <sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### 라이선스 및 면책 조항

**다음에서 확인하세요:** <sup>[[13]](#references)</sup>

[HackTricks Values 및 FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub 통계

![HackTricks Cloud GitHub 통계](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[14]](#references)</sup>

## 참고 자료

- [1] [Instagram의 Nacho Piera (@ppieranacho)](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Docker container run reference](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Docker Compose up reference](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve command](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone documentation](https://git-scm.com/docs/git-clone)
- [9] [Git checkout documentation](https://git-scm.com/docs/git-checkout)
- [10] [Git pull documentation](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values 및 FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [HackTricks Cloud용 Repobeats 통계 그래픽](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
