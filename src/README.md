# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logo và chuyển động của Hacktricks do_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_ thiết kế._<sup>[[1]](#references)</sup>

### Chạy HackTricks Cloud cục bộ

Quy trình dưới đây tuân theo các thao tác `clone`, `checkout` và `pull` được Git ghi nhận, cùng các nhánh ngôn ngữ đã công bố và cấu hình container của repository.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

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
# "vi" for Vietnamese
# "zh" for Chinese

# Run the docker container indicating the path to the hacktricks-cloud folder
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $HT_LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```

Lệnh container tuân theo giao diện `run` được Docker tài liệu hóa và sử dụng máy chủ xem trước HTTP của mdBook; repository ánh xạ cổng 3000 của container sang cổng 3377 trên máy cục bộ.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Bản sao HackTricks Cloud trên máy cục bộ của bạn sẽ **khả dụng tại [http://localhost:3377](http://localhost:3377)** sau một phút.<sup>[[2]](#references)</sup>

Ngoài ra, nếu có Docker Compose, hãy chạy lệnh này từ thư mục gốc của repository:<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

The bundled `docker-compose.yml` phục vụ branch hiện đang được checkout của bạn tại [http://localhost:3377](http://localhost:3377) với tính năng tự tải lại.<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Phương pháp Pentesting CI/CD**

**Trong Phương pháp CI/CD của HackTricks, bạn sẽ tìm thấy cách pentest cơ sở hạ tầng liên quan đến các hoạt động CI/CD.** Đọc trang sau để **tìm hiểu nhập môn:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Phương pháp Pentesting Cloud

**Trong Phương pháp Cloud của HackTricks, bạn sẽ tìm thấy cách pentest các môi trường cloud.** Đọc trang sau để **tìm hiểu nhập môn:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Giấy phép & Tuyên bố miễn trừ trách nhiệm

**Xem tại:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Thống kê GitHub

![Thống kê GitHub của HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## References

- [1] [Nacho Piera (@ppieranacho) trên Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Kho lưu trữ HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Các branch của HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [docker-compose.yml của HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Tài liệu tham khảo về lệnh chạy Docker container](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Tài liệu tham khảo về lệnh Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Lệnh mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Tài liệu Git clone](https://git-scm.com/docs/git-clone)
- [9] [Tài liệu Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Tài liệu Git pull](https://git-scm.com/docs/git-pull)
- [11] [Phương pháp Pentesting CI/CD của HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Phương pháp Pentesting Cloud của HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [Giá trị & FAQ của HackTricks](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Biểu đồ thống kê Repobeats của HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)
{{#include ./banners/hacktricks-training.md}}
