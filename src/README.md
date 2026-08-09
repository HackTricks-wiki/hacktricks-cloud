# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Hacktricks logos & motion designed by_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Run HackTricks Cloud Locally

The workflow below follows Git's documented `clone`, `checkout`, and `pull` operations and the repository's published language branches and container setup.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

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

The container command follows Docker's documented `run` interface and uses mdBook's HTTP preview server; the repository maps the container's port 3000 to local port 3377.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Your local copy of HackTricks Cloud will be **available at [http://localhost:3377](http://localhost:3377)** after a minute.<sup>[[2]](#references)</sup>

Alternatively, if you have Docker Compose, run this from the repository root:<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

The bundled `docker-compose.yml` serves your currently checked-out branch at [http://localhost:3377](http://localhost:3377) with live reload.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Pentesting CI/CD Methodology**

**In the HackTricks CI/CD Methodology you will find how to pentest infrastructure related to CI/CD activities.** Read the following page for an **introduction:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Pentesting Cloud Methodology

**In the HackTricks Cloud Methodology you will find how to pentest cloud environments.** Read the following page for an **introduction:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### License & Disclaimer

**Check them in:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Github Stats

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## References

- [1] [Nacho Piera (@ppieranacho) on Instagram](https://www.instagram.com/ppieranacho/)
- [2] [HackTricks-wiki/hacktricks-cloud repository](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [HackTricks Cloud branches](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [HackTricks Cloud docker-compose.yml](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Docker container run reference](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Docker Compose up reference](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [mdBook serve command](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Git clone documentation](https://git-scm.com/docs/git-clone)
- [9] [Git checkout documentation](https://git-scm.com/docs/git-checkout)
- [10] [Git pull documentation](https://git-scm.com/docs/git-pull)
- [11] [HackTricks CI/CD Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [HackTricks Cloud Pentesting Methodology](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Repobeats statistics graphic for HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
