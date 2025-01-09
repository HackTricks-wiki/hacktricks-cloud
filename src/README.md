# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks 로고 및 모션 디자인_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_에 의해 제작되었습니다._

### HackTricks Cloud를 로컬에서 실행하기
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
당신의 로컬 HackTricks Cloud 복사본은 **1분 후에 [http://localhost:3377](http://localhost:3377)** 에서 **사용 가능**합니다.

### **펜테스팅 CI/CD 방법론**

**HackTricks CI/CD 방법론에서는 CI/CD 활동과 관련된 인프라를 펜테스트하는 방법을 찾을 수 있습니다.** 다음 페이지를 읽어 **소개를 확인하세요:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### 펜테스팅 클라우드 방법론

**HackTricks Cloud 방법론에서는 클라우드 환경을 펜테스트하는 방법을 찾을 수 있습니다.** 다음 페이지를 읽어 **소개를 확인하세요:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### 라이센스 및 면책 조항

**다음에서 확인하세요:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github 통계

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
