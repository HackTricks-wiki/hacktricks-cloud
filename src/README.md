# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks के logos और motion को_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_ने डिज़ाइन किया है।_

### HackTricks Cloud को स्थानीय रूप से चलाएं
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
आपकी HackTricks Cloud की स्थानीय कॉपी एक मिनट बाद **[http://localhost:3377](http://localhost:3377)** पर **उपलब्ध होगी**।

वैकल्पिक रूप से, यदि आपके पास Docker Compose है, तो इसे repository root से चलाएँ:
```bash
docker compose up
```
Bundled `docker-compose.yml` आपके वर्तमान में checkout किए गए branch को [http://localhost:3377](http://localhost:3377) पर live reload के साथ serve करता है।

### **Pentesting CI/CD कार्यप्रणाली**

**HackTricks CI/CD कार्यप्रणाली में आपको CI/CD activities से संबंधित infrastructure को pentest करने का तरीका मिलेगा।** एक **परिचय** के लिए निम्नलिखित page पढ़ें:

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud कार्यप्रणाली

**HackTricks Cloud कार्यप्रणाली में आपको cloud environments को pentest करने का तरीका मिलेगा।** एक **परिचय** के लिए निम्नलिखित page पढ़ें:

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License और Disclaimer

**इन्हें यहाँ देखें:**

[HackTricks Values और FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### GitHub Stats

![HackTricks Cloud GitHub Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
