# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logos & motion designed by_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### 本地运行 HackTricks Cloud
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
您的本地 HackTricks Cloud 副本将在 **[http://localhost:3377](http://localhost:3377)** 一分钟后可用。

### **渗透测试 CI/CD 方法论**

**在 HackTricks CI/CD 方法论中，您将找到如何对与 CI/CD 活动相关的基础设施进行渗透测试。** 请阅读以下页面以获取 **介绍：**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### 渗透测试云方法论

**在 HackTricks 云方法论中，您将找到如何对云环境进行渗透测试。** 请阅读以下页面以获取 **介绍：**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### 许可证与免责声明

**请查看：**

[HackTricks 值与常见问题](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github 统计

![HackTricks Cloud Github 统计](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
