# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos e animação do Hacktricks criados por_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._

### Execute o HackTricks Cloud localmente
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
Sua cópia local do HackTricks Cloud estará **disponível em [http://localhost:3377](http://localhost:3377)** após um minuto.

Como alternativa, se você tiver o Docker Compose, execute isto na raiz do repositório:
```bash
docker compose up
```
O `docker-compose.yml` incluído disponibiliza sua branch atualmente checked-out em [http://localhost:3377](http://localhost:3377) com live reload.

### **Metodologia de Pentesting de CI/CD**

**Na HackTricks CI/CD Methodology, você encontrará informações sobre como fazer pentesting de infraestrutura relacionada a atividades de CI/CD.** Leia a página a seguir para uma **introdução:**

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia de Pentesting de Cloud

**Na HackTricks Cloud Methodology, você encontrará informações sobre como fazer pentesting de ambientes cloud.** Leia a página a seguir para uma **introdução:**

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licença e Isenção de Responsabilidade

**Confira em:**

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Estatísticas do GitHub

![Estatísticas do GitHub do HackTricks](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
