# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logo 和动态效果由_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_设计。_

### 在本地运行 HackTricks Cloud
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
你的本地 HackTricks Cloud 副本将在一分钟后**可通过 [http://localhost:3377](http://localhost:3377) 访问**。

或者，如果你有 Docker Compose，请在仓库根目录运行以下命令：
```bash
docker compose up
```
随附的 `docker-compose.yml` 会通过 [http://localhost:3377](http://localhost:3377) 提供当前检出的 branch，并支持 live reload。

### **Pentesting CI/CD Methodology**

**在 HackTricks CI/CD Methodology 中，你将了解如何对与 CI/CD 活动相关的基础设施进行 pentest。** 阅读以下页面获取**简介：**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**在 HackTricks Cloud Methodology 中，你将了解如何对 cloud environments 进行 pentest。** 阅读以下页面获取**简介：**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License & Disclaimer

**请在以下位置查看：**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Stats

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
