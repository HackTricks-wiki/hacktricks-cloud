# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricksのロゴとモーションは_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_によってデザインされています。_

### HackTricks Cloudをローカルで実行する
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
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git checkout $LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
あなたのローカルコピーのHackTricks Cloudは、**[http://localhost:3377](http://localhost:3377)**で**1分後に利用可能になります。**

### **ペンテストCI/CDメソッド**

**HackTricks CI/CDメソッドでは、CI/CD活動に関連するインフラストラクチャのペンテスト方法を見つけることができます。** 次のページを読んで**イントロダクションを確認してください：**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### ペンテストクラウドメソッド

**HackTricks Cloudメソッドでは、クラウド環境のペンテスト方法を見つけることができます。** 次のページを読んで**イントロダクションを確認してください：**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### ライセンスと免責事項

**以下で確認してください：**

[HackTricksの価値とFAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github統計

![HackTricks Cloud Github統計](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
