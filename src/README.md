# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Логотипи Hacktricks та анімація розроблені_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Запустіть HackTricks Cloud локально
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
Ваша локальна копія HackTricks Cloud буде **доступна за [http://localhost:3377](http://localhost:3377)** через хвилину.

### **Методологія Pentesting CI/CD**

**У методології HackTricks CI/CD ви знайдете, як проводити тестування на проникнення в інфраструктуру, пов'язану з CI/CD активностями.** Прочитайте наступну сторінку для **вступу:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Методологія Pentesting Cloud

**У методології HackTricks Cloud ви знайдете, як проводити тестування на проникнення в хмарні середовища.** Прочитайте наступну сторінку для **вступу:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Ліцензія та відмова від відповідальності

**Перевірте їх у:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Статистика Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
