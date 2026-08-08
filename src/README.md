# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Логотипи та анімація HackTricks розроблені_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### Запуск HackTricks Cloud локально

Наведений нижче робочий процес відповідає задокументованим у Git операціям `clone`, `checkout` і `pull`, а також опублікованим мовним гілкам репозиторію та налаштуванню контейнера. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
Команда контейнера відповідає документованому інтерфейсу `run` Docker і використовує HTTP-сервер попереднього перегляду mdBook; repository перенаправляє порт контейнера 3000 на локальний порт 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Ваша локальна копія HackTricks Cloud буде **доступна за адресою [http://localhost:3377](http://localhost:3377)** через хвилину. <sup>[[3]](#references)</sup>

Альтернативно, якщо у вас є Docker Compose, виконайте цю команду з кореня repository: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Вбудований `docker-compose.yml` обслуговує поточну checkout-гілку за адресою [http://localhost:3377](http://localhost:3377) із live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Методологія Pentesting CI/CD**

**У HackTricks CI/CD Methodology ви знайдете інформацію про те, як проводити pentesting інфраструктури, пов’язаної з CI/CD-активностями.** Ознайомтеся з цією сторінкою для **вступу:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Методологія Pentesting Cloud

**У HackTricks Cloud Methodology ви знайдете інформацію про те, як проводити pentesting cloud-середовищ.** Ознайомтеся з цією сторінкою для **вступу:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Ліцензія та відмова від відповідальності

**Ознайомтеся з ними тут:** <sup>[[14]](#references)</sup>

[Цінності HackTricks та FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Статистика Github

![Статистика HackTricks Cloud на Github](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Посилання

- [1] [Nacho Piera (@ppieranacho) в Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Банер навчання та підтримки HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [Репозиторій HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [Гілки HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [docker-compose.yml HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Довідка щодо запуску контейнера Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Довідка щодо команди Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [Довідка щодо команди mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Документація Git clone](https://git-scm.com/docs/git-clone)
- [10] [Документація Git checkout](https://git-scm.com/docs/git-checkout)
- [11] [Документація Git pull](https://git-scm.com/docs/git-pull)
- [12] [Методологія Pentesting CI/CD від HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [Методологія Pentesting Cloud від HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [Цінності HackTricks та FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Графік статистики Repobeats для HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
