# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricksのロゴとモーションのデザイン：_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### HackTricks Cloudをローカルで実行する
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
HackTricks Cloud のローカルコピーは、1分後に **[http://localhost:3377](http://localhost:3377)** で利用可能になります。

または、Docker Compose がある場合は、repository root から次を実行してください:
```bash
docker compose up
```
同梱の `docker-compose.yml` は、現在 checkout しているブランチを live reload 付きで [http://localhost:3377](http://localhost:3377) に提供します。

### **Pentesting CI/CD 方法論**

**HackTricks CI/CD 方法論では、CI/CD に関連するインフラを pentest する方法を説明しています。** **導入編：**として以下のページをお読みください。

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud 方法論

**HackTricks Cloud 方法論では、Cloud 環境を pentest する方法を説明しています。** **導入編：**として以下のページをお読みください。

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### ライセンスと免責事項

**以下で確認してください：**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub Stats

![HackTricks Cloud GitHub Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
