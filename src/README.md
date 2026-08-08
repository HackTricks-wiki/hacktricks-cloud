# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logos और motion को_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_ ने design किया है।_ <sup>[[1]](#references)[[3]](#references)</sup>

### HackTricks Cloud को स्थानीय रूप से चलाएँ

नीचे दिया गया workflow Git के documented `clone`, `checkout`, और `pull` operations तथा repository की published language branches और container setup का अनुसरण करता है। <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
container command Docker के documented `run` interface का पालन करता है और mdBook के HTTP preview server का उपयोग करता है; repository container के port 3000 को local port 3377 से map करता है। <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

आपकी HackTricks Cloud की local copy एक मिनट बाद **[http://localhost:3377](http://localhost:3377)** पर उपलब्ध होगी। <sup>[[3]](#references)</sup>

वैकल्पिक रूप से, यदि आपके पास Docker Compose है, तो इसे repository root से चलाएँ: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
Bundled `docker-compose.yml` आपके वर्तमान में checkout किए गए branch को live reload के साथ [http://localhost:3377](http://localhost:3377) पर serve करता है। <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Pentesting CI/CD Methodology**

**HackTricks CI/CD Methodology में आपको CI/CD activities से संबंधित infrastructure को pentest करने का तरीका मिलेगा।** **परिचय** के लिए निम्नलिखित page पढ़ें: <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**HackTricks Cloud Methodology में आपको cloud environments को pentest करने का तरीका मिलेगा।** **परिचय** के लिए निम्नलिखित page पढ़ें: <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### लाइसेंस और अस्वीकरण

**इन्हें यहां देखें:** <sup>[[14]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github आँकड़े

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## संदर्भ

- [1] [Nacho Piera (@ppieranacho) on Instagram](https://www.instagram.com/ppieranacho/)
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
