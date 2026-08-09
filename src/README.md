# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logo 和动态效果由_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_设计_。<sup>[[1]](#references)</sup>

### 在本地运行 HackTricks Cloud

以下工作流程遵循 Git 文档中说明的 `clone`、`checkout` 和 `pull` 操作，以及仓库已发布的语言分支和容器设置。<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
容器命令遵循 Docker 文档中的 `run` 接口，并使用 mdBook 的 HTTP 预览服务器；该仓库将容器的 3000 端口映射到本地 3377 端口。<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

一分钟后，你的本地 HackTricks Cloud 副本将**可通过 [http://localhost:3377](http://localhost:3377) 访问**。<sup>[[2]](#references)</sup>

或者，如果你有 Docker Compose，请从仓库根目录运行以下命令：<sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
捆绑的 `docker-compose.yml` 会通过实时重载，在 [http://localhost:3377](http://localhost:3377) 提供当前已 checkout 分支的内容。<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD 方法论**

**在 HackTricks CI/CD 方法论中，你将了解如何对与 CI/CD 活动相关的基础设施执行 pentest。** 阅读以下页面以了解**简介：**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud 方法论

**在 HackTricks Cloud 方法论中，你将了解如何对 cloud 环境执行 pentest。** 阅读以下页面以了解**简介：**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### 许可证与免责声明

**请在此查看：**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub 统计

![HackTricks Cloud GitHub 统计](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## 参考资料

- [1] [Instagram 上的 Nacho Piera (@ppieranacho)](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud 分支](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Docker 容器运行参考](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Docker Compose up 参考](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve 命令](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone 文档](https://git-scm.com/docs/git-clone)
- [9] [Git checkout 文档](https://git-scm.com/docs/git-checkout)
- [10] [Git pull 文档](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting 方法论](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting 方法论](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [HackTricks Cloud 的 Repobeats 统计图](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
