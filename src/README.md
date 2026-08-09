# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logos e animação do Hacktricks criados por_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Executar o HackTricks Cloud localmente

O fluxo de trabalho abaixo segue as operações documentadas pelo Git de `clone`, `checkout` e `pull`, além das branches de idioma publicadas pelo repositório e da configuração de container.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>
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
O comando do container segue a interface `run` documentada pelo Docker e usa o servidor de preview HTTP do mdBook; o repositório mapeia a porta 3000 do container para a porta local 3377.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Sua cópia local do HackTricks Cloud estará **disponível em [http://localhost:3377](http://localhost:3377)** após um minuto.<sup>[[2]](#references)</sup>

Como alternativa, se você tiver Docker Compose, execute isto a partir da raiz do repositório:<sup>[[2]](#references)[[6]](#references)</sup>
```bash
docker compose up
```
O `docker-compose.yml` incluído serve sua branch atualmente selecionada em [http://localhost:3377](http://localhost:3377) com live reload.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Metodologia de Pentesting de CI/CD**

**Na Metodologia de CI/CD do HackTricks, você encontrará como fazer pentesting da infraestrutura relacionada às atividades de CI/CD.** Leia a página a seguir para uma **introdução:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Metodologia de Pentesting Cloud

**Na Metodologia Cloud do HackTricks, você encontrará como fazer pentesting de ambientes cloud.** Leia a página a seguir para uma **introdução:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Licença e Aviso Legal

**Consulte-os em:**<sup>[[13]](#references)</sup>

[Valores e FAQ do HackTricks](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Estatísticas do Github

![Estatísticas do Github do HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## Referências

- [1] [Nacho Piera (@ppieranacho) no Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Repositório HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Branches do HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [docker-compose.yml do HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Referência para executar contêineres Docker](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Referência do Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Comando mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Documentação do Git clone](https://git-scm.com/docs/git-clone)
- [9] [Documentação do Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Documentação do Git pull](https://git-scm.com/docs/git-pull)
- [11] [Metodologia de Pentesting de CI/CD do HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Metodologia de Pentesting Cloud do HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [Valores e FAQ do HackTricks](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Gráfico de estatísticas do Repobeats para o HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
