# HackTricks Cloud

<figure><img src="images/cloud.gif" alt=""><figcaption></figcaption></figure>

_Logo & hiệu ứng động của Hacktricks được thiết kế bởi_ [_@ppieranacho_](https://www.instagram.com/ppieranacho/)_._<sup>[[1]](#references)</sup>

### Chạy HackTricks Cloud trên máy cá nhân (Local)

Quy trình dưới đây sử dụng các lệnh `clone`, `checkout`, `pull` tiêu chuẩn của Git, cùng với hệ thống nhánh ngôn ngữ và cấu hình container đã được công bố của repository.<sup>[[2]](#references)[[3]](#references)[[8]](#references)[[9]](#references)[[10]](#references)</sup>

```bash
# Tải phiên bản mới nhất của hacktricks cloud
git clone https://github.com/HackTricks-wiki/hacktricks-cloud

# Chọn ngôn ngữ bạn muốn sử dụng
export HT_LANG="master" # Để "master" cho bản tiếng Anh
# "af" cho tiếng Afrikaans
# "de" cho tiếng Đức
# "el" cho tiếng Hy Lạp
# "es" cho tiếng Tây Ban Nha
# "fr" cho tiếng Pháp
# "hi" cho tiếng Hindi
# "it" cho tiếng Ý
# "ja" cho tiếng Nhật
# "ko" cho tiếng Hàn
# "pl" cho tiếng Ba Lan
# "pt" cho tiếng Bồ Đào Nha
# "sr" cho tiếng Serbia
# "sw" cho tiếng Swahili
# "tr" cho tiếng Thổ Nhĩ Kỳ
# "uk" cho tiếng Ukraina
# "zh" cho tiếng Trung
# "vi" cho tiếng Việt

# Chạy container docker, chỉ định đường dẫn tới thư mục hacktricks-cloud
docker run -d --rm --platform linux/amd64 -p 3377:3000 --name hacktricks_cloud -v $(pwd)/hacktricks-cloud:/app ghcr.io/hacktricks-wiki/hacktricks-cloud/translator-image bash -c "mkdir -p ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts && cd /app && git checkout $HT_LANG && git pull && MDBOOK_PREPROCESSOR__HACKTRICKS__ENV=dev mdbook serve --hostname 0.0.0.0"
```

Lệnh container ở trên tuân theo cú pháp `run` tiêu chuẩn của Docker và dùng máy chủ xem trước (preview server) HTTP của mdBook; repository đã cấu hình để nối cổng 3000 bên trong container ra cổng 3377 trên máy của bạn.<sup>[[4]](#references)[[5]](#references)[[7]](#references)</sup>

Bản sao cục bộ của HackTricks Cloud sẽ **có thể truy cập tại [http://localhost:3377](http://localhost:3377)** sau khoảng một phút.<sup>[[2]](#references)</sup>

Ngoài ra, nếu máy bạn có Docker Compose, bạn có thể chạy lệnh sau từ thư mục gốc của repository:<sup>[[2]](#references)[[6]](#references)</sup>

```bash
docker compose up
```

File `docker-compose.yml` có sẵn trong repo sẽ phát (serve) nhánh bạn đang checkout tại [http://localhost:3377](http://localhost:3377), kèm chức năng tự tải lại khi có thay đổi (live reload).<sup>[[2]](#references)[[6]](#references)[[7]](#references)</sup>

### **Phương pháp luận Pentest CI/CD**

**Trong mục HackTricks CI/CD Methodology, bạn sẽ tìm thấy cách kiểm tra bảo mật (pentest) các hạ tầng liên quan đến hoạt động CI/CD.** Đọc trang sau để có phần **giới thiệu:**<sup>[[11]](#references)</sup>

[pentesting-ci-cd-methodology.md](pentesting-ci-cd/pentesting-ci-cd-methodology.md)

### Phương pháp luận Pentest Cloud

**Trong mục HackTricks Cloud Methodology, bạn sẽ tìm thấy cách kiểm tra bảo mật (pentest) các môi trường cloud.** Đọc trang sau để có phần **giới thiệu:**<sup>[[12]](#references)</sup>

[pentesting-cloud-methodology.md](pentesting-cloud/pentesting-cloud-methodology.md)

### Giấy phép & Tuyên bố miễn trừ trách nhiệm (License & Disclaimer)

**Xem chi tiết tại:**<sup>[[13]](#references)</sup>

[HackTricks Values & FAQ](https://app.gitbook.com/s/-L_2uGJGU7AVNRcqRvEi/welcome/hacktricks-values-and-faq)

### Thống kê Github

![HackTricks Cloud Github Stats](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)<sup>[[14]](#references)</sup>

## Tham khảo (References)

- [1] [Nacho Piera (@ppieranacho) trên Instagram](https://www.instagram.com/ppieranacho/)
- [2] [Repository HackTricks-wiki/hacktricks-cloud](https://github.com/HackTricks-wiki/hacktricks-cloud)
- [3] [Các nhánh của HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/branches/all)
- [4] [File docker-compose.yml của HackTricks Cloud](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/docker-compose.yml)
- [5] [Tài liệu Docker container run](https://docs.docker.com/reference/cli/docker/container/run/)
- [6] [Tài liệu Docker Compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
- [7] [Lệnh mdBook serve](https://rust-lang.github.io/mdBook/cli/serve.html)
- [8] [Tài liệu Git clone](https://git-scm.com/docs/git-clone)
- [9] [Tài liệu Git checkout](https://git-scm.com/docs/git-checkout)
- [10] [Tài liệu Git pull](https://git-scm.com/docs/git-pull)
- [11] [Phương pháp luận Pentest CI/CD của HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-ci-cd/pentesting-ci-cd-methodology.md)
- [12] [Phương pháp luận Pentest Cloud của HackTricks](https://github.com/HackTricks-wiki/hacktricks-cloud/blob/master/src/pentesting-cloud/pentesting-cloud-methodology.md)
- [13] [HackTricks Values & FAQ](https://book.hacktricks.wiki/en/welcome/hacktricks-values-and-faq.html)
- [14] [Biểu đồ thống kê Repobeats cho HackTricks Cloud](https://repobeats.axiom.co/api/embed/1dfdbb0435f74afa9803cd863f01daac17cda336.svg)

{{#include ./banners/hacktricks-training.md}}
