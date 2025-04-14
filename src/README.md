# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logos & motion designed by_ [_@ppiernacho_](https://www.instagram.com/ppieranacho/)_._

### Run HackTricks Cloud Locally

```bash
# Download latest version of hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud

# Select the language you want to use
export LANG="master" # Leave master for english
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
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "cd /app && git checkout $LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```

Your local copy of HackTricks Cloud will be **available at [http://localhost:3377](http://localhost:3377)** after a minute.

### **Pentesting CI/CD Methodology**

**In the HackTricks CI/CD Methodology you will find how to pentest infrastructure related to CI/CD activities.** Read the following page for an **introduction:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**In the HackTricks Cloud Methodology you will find how to pentest cloud environments.** Read the following page for an **introduction:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License & Disclaimer

**Check them in:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Stats

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
