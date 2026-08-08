# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks のロゴとモーションのデザイン:_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_。_ <sup>[[1]](#references)[[3]](#references)</sup>

### HackTricks Cloud をローカルで実行する

以下のワークフローは、Git によって文書化された `clone`、`checkout`、`pull` 操作と、リポジトリで公開されている言語ブランチおよびコンテナのセットアップに従います。 <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
コンテナコマンドは Docker の文書化された `run` インターフェースに従い、mdBook の HTTP プレビューサーバーを使用します。リポジトリでは、コンテナのポート 3000 がローカルポート 3377 にマッピングされます。 <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

ローカルの HackTricks Cloud は、1 分後に **[http://localhost:3377](http://localhost:3377)** で利用可能になります。 <sup>[[3]](#references)</sup>

または、Docker Compose がある場合は、リポジトリのルートで次を実行します。 <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
同梱の `docker-compose.yml` は、現在 checkout している branch を live reload 付きで [http://localhost:3377](http://localhost:3377) に提供します。 <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Pentesting CI/CD Methodology**

**HackTricks CI/CD Methodology では、CI/CD activities に関連する infrastructure を pentest する方法を確認できます。** 以下のページで **introduction** をお読みください: <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**HackTricks Cloud Methodology では、cloud environments を pentest する方法を確認できます。** 以下のページで **introduction** をお読みください: <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License & Disclaimer

**こちらでご確認ください:** <sup>[[14]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub Stats

![HackTricks Cloud GitHub Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## References

- [1] [Instagram の Nacho Piera (@ppieranacho)](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks Cloud training and support banner](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [HackTricks-wiki/hacktricks-cloud repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [HackTricks Cloud branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Docker container run reference](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Docker Compose up reference](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [mdBook serve command](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Git clone documentation](https://git-scm.com/docs/git-clone)
- [10] [Git checkout documentation](https://git-scm.com/docs/git-checkout)
- [11] [Git pull documentation](https://git-scm.com/docs/git-pull)
- [12] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Repobeats statistics graphic for HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
