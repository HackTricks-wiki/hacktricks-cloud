# HackTricks Cloud

{{#include ./banners/hacktricks-training.md}}

<sup>[[2]](#references)</sup>

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos e animação do Hacktricks projetados por_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._ <sup>[[1]](#references)[[3]](#references)</sup>

### Executar o HackTricks Cloud localmente

O fluxo de trabalho abaixo segue as operações documentadas pelo Git de `clone`, `checkout` e `pull`, além das branches de idioma publicadas pelo repositório e da configuração do container. <sup>[[3]](#references)[[4]](#references)[[9]](#references)[[10]](#references)[[11]](#references)</sup>
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
O comando do container segue a interface `run` documentada pelo Docker e usa o servidor de preview HTTP do mdBook; o repositório mapeia a porta 3000 do container para a porta local 3377. <sup>[[5]](#references)[[6]](#references)[[8]](#references)</sup>

Sua cópia local do HackTricks Cloud estará **disponível em [http://localhost:3377](http://localhost:3377)** após um minuto. <sup>[[3]](#references)</sup>

Como alternativa, se você tiver Docker Compose, execute isto na raiz do repositório: <sup>[[3]](#references)[[7]](#references)</sup>
```bash
docker compose up
```
O `docker-compose.yml` incluído disponibiliza sua branch atualmente selecionada em [http://localhost:3377](http://localhost:3377) com live reload. <sup>[[3]](#references)[[7]](#references)[[8]](#references)</sup>

### **Metodologia de Pentesting de CI/CD**

**Na Metodologia de CI/CD do HackTricks, você encontrará informações sobre como realizar pentesting em infraestruturas relacionadas às atividades de CI/CD.** Leia a página a seguir para uma **introdução:** <sup>[[12]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia de Pentesting de Cloud

**Na Metodologia de Cloud do HackTricks, você encontrará informações sobre como realizar pentesting em ambientes de cloud.** Leia a página a seguir para uma **introdução:** <sup>[[13]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licença e Isenção de responsabilidade

**Consulte-as em:** <sup>[[14]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Estatísticas do Github

![Estatísticas do Github do HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg) <sup>[[15]](#references)</sup>

## Referências

- [1] [Nacho Piera (@ppieranacho) no Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Banner de treinamento e suporte do HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/banners/hacktricks-training.md)
- [3] [Repositório HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [4] [Branches do HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [5] [docker-compose.yml do HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [6] [Referência de execução de contêineres do Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [7] [Referência do Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [8] [Comando mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [9] [Documentação do Git clone](https://git-scm.com/docs/git-clone)
- [10] [Documentação do Git checkout](https://git-scm.com/docs/git-checkout)
- [11] [Documentação do Git pull](https://git-scm.com/docs/git-pull)
- [12] [Metodologia de Pentesting de CI/CD do HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [13] [Metodologia de Pentesting de Cloud do HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [14] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [15] [Gráfico de estatísticas do Repobeats para o HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
