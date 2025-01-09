# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks लोगो और मोशन डिज़ाइन_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_ द्वारा_._

### HackTricks Cloud को स्थानीय रूप से चलाएँ
```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud
# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```
आपकी स्थानीय कॉपी HackTricks Cloud **एक मिनट बाद [http://localhost:3377](http://localhost:3377)** पर **उपलब्ध होगी।**

### **Pentesting CI/CD Methodology**

**HackTricks CI/CD Methodology में आपको CI/CD गतिविधियों से संबंधित बुनियादी ढांचे का pentest करने का तरीका मिलेगा।** एक **परिचय के लिए निम्नलिखित पृष्ठ पढ़ें:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**HackTricks Cloud Methodology में आपको क्लाउड वातावरण का pentest करने का तरीका मिलेगा।** एक **परिचय के लिए निम्नलिखित पृष्ठ पढ़ें:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License & Disclaimer

**इन्हें देखें:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Stats

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
