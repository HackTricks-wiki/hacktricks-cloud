# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks のロゴとモーションのデザイン:_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)</sup>

### HackTricks Cloud をローカルで実行する

以下のワークフローは、Git で文書化されている `clone`、`checkout`、`pull` の操作と、リポジトリで公開されている言語ブランチおよびコンテナ設定に従います。 <sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
コンテナコマンドは Docker のドキュメントに記載された `run` インターフェースに従い、mdBook の HTTP preview server を使用します。repository はコンテナのポート 3000 をローカルポート 3377 にマッピングします。 <sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

ローカルの HackTricks Cloud は、1 分後に **[http://localhost:3377](http://localhost:3377)** で**利用可能になります**。 <sup>[[2]](#references)</sup>

また、Docker Compose がある場合は、repository のルートで次を実行します。 <sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
同梱の `docker-compose.yml` は、現在 checkout しているブランチを [http://localhost:3377](http://localhost:3377) でライブリロード付きで提供します。 <sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD Methodology**

**HackTricks CI/CD Methodology では、CI/CD activities に関連するインフラストラクチャを pentest する方法を説明しています。** 以下のページで**概要**を確認してください。 <sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**HackTricks Cloud Methodology では、cloud environments を pentest する方法を説明しています。** 以下のページで**概要**を確認してください。 <sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### ライセンスと免責事項

**以下で確認してください:** <sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub 統計

![HackTricks Cloud GitHub 統計](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[14]](#references)</sup>

## 参照

- [1] [Instagram の Nacho Piera (@ppieranacho)](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud リポジトリ](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud のブランチ](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud の docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Docker コンテナの run リファレンス](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Docker Compose up リファレンス](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve コマンド](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone ドキュメント](https://git-scm.com/docs/git-clone)
- [9] [Git checkout ドキュメント](https://git-scm.com/docs/git-checkout)
- [10] [Git pull ドキュメント](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [HackTricks Cloud の Repobeats 統計グラフィック](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
