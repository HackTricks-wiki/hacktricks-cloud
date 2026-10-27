# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks のロゴとモーションのデザイン：_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_。_<sup>[[1]](#references)</sup>

### HackTricks Cloud をローカルで実行する

以下のワークフローでは、Git でドキュメント化されている `clone`、`checkout`、`pull` 操作と、リポジトリで公開されている言語ブランチおよびコンテナのセットアップを使用します。<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

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
# "vi" for Vietnamese
# "zh" for Chinese

# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $HT_LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```

コンテナコマンドは Docker のドキュメントに記載された `run` インターフェースに従い、mdBook の HTTP プレビューサーバーを使用します。リポジトリでは、コンテナのポート 3000 がローカルのポート 3377 に割り当てられています。<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

1 分ほどすると、ローカルの HackTricks Cloud が **[http://localhost:3377](http://localhost:3377)** で利用できるようになります。<sup>[[2]](#references)</sup>

または、Docker Compose がある場合は、リポジトリのルートから次を実行してください。<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

同梱の `docker-compose.yml` は、現在チェックアウトしているブランチを [http://localhost:3377](http://localhost:3377) でライブリロード付きで配信します。<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD 方法論**

**HackTricks CI/CD 方法論では、CI/CD のアクティビティに関連するインフラをどのように pentest するかを紹介しています。** 以下のページで**概要**を確認してください。<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud 方法論

**HackTricks Cloud 方法論では、クラウド環境をどのように pentest するかを紹介しています。** 以下のページで**概要**を確認してください。<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### ライセンスと免責事項

**こちらでご確認ください：**<sup>[[13]](#references)</sup>

[HackTricks の価値観と FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub 統計

![HackTricks Cloud の GitHub 統計](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## References

- [1] [Nacho Piera (@ppieranacho) の Instagram アカウント](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud リポジトリ](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud のブランチ](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud の docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Docker コンテナ run のリファレンス](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Docker Compose up のリファレンス](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve コマンド](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone のドキュメント](https://git-scm.com/docs/git-clone)
- [9] [Git checkout のドキュメント](https://git-scm.com/docs/git-checkout)
- [10] [Git pull のドキュメント](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting 方法論](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting 方法論](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks の価値観と FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [HackTricks Cloud の Repobeats 統計グラフィック](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)
{{#include ./banners/hacktricks-training.md}}
