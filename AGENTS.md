# AGENTS.md

Bu repository üzerinde çalışacak gelecekteki agent'lar için yönergeler.

## Repository Context

Bu, HackTricks Cloud mdBook repository'sidir. İlgili ana book şu konumda bulunur:

`/Users/carlospolop/git/hacktricks`

Paylaşılan theme/search davranışındaki değişikliklerin çoğunlukla her iki repository'ye de uygulanması gerekir.

## Search Index Loading Contract

Özel search UI şu konumda bulunur:

`theme/ht_searcher.js`

Ayrıca oluşturulmuş bir kopya şu konumda bulunabilir:

`book/theme/ht_searcher.js`

Production zaten oluşturulmuş `book/` dizinini deploy ediyorsa her iki kopyayı da güncelleyin veya book'u yeniden build edin.

Search index yükleme sırası önemlidir ve maliyete duyarlıdır:

1. GitHub repository'sindeki her language-specific ve fallback search index'i yükleyin:
`HackTricks-wiki/hacktricks-searchindex`
2. Yalnızca GitHub-hosted tüm adaylar başarısız olursa aynı-origin mdBook çıktısına fallback yapın.

Yerel `/searchindex.js` fallback'ini `searchindex-cloud-en.js.gz` gibi herhangi bir GitHub-hosted fallback'in önüne koymayın. Production'da `cloud.hacktricks.wiki` üzerinden `searchindex.js` sunmak maliyetlidir.

Bu repo için beklenen yerel fallback:

`/searchindex.js`

Bu repo için ana-book fallback'i:

`/searchindex-book.js`

Bu dosya yalnızca bir fallback'tir. Primary source, `HackTricks-wiki/hacktricks-searchindex` içindeki uzak `searchindex-<lang>.js.gz` ve `searchindex-cloud-<lang>.js.gz` dosyaları olarak kalmalıdır.

## Search Index Publishing

Şifrelenmiş sıkıştırılmış search index'lerini `HackTricks-wiki/hacktricks-searchindex` repository'sine publish eden workflow'lar şunlardır:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Oluşturulan source dosyası `book/searchindex.js`'dir. Publish edilen uzak artifact adları şunlardır:

- `searchindex-cloud-v2-en.json.gz` (tercih edilen compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (tercih edilen compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader, compact v2 artifact'ini tercih eder ve `.js.gz` artifact'ini legacy fallback olarak korur. Her ikisi de `theme/ht_searcher.js` içinde tanımlanan key kullanılarak XOR-encrypted gzip payload'larıdır.

Loader lazy kalmalıdır: normal page navigation, ziyaretçi search'ü açana veya kullanana kadar search worker oluşturmamalı veya index download etmemelidir. Remote compressed response'lar origin başına 24 saat boyunca Cache Storage'da saklanır; böylece sonraki sayfalar bunları yeniden kullanabilir. Süresi dolmuş bir entry yenilenirken başarısız olursa stale-cache fallback'ini koruyun.

## Build And Validation

Yaygın local kontroller:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` başarısız olursa şunları kontrol edin:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Arama yapmak için `rg` kullanmayı tercih edin.
- Açıkça istenmediği sürece oluşturulan `book/` çıktısını commit'lerin dışında tutun. Zaten oluşturulmuş sayfaların hemen düzeltilmesi gerektiğinde search loader düzeltmeleri istisnadır.
- Paylaşılan theme davranışını değiştiriyorsanız `/Users/carlospolop/git/hacktricks` içindeki eşleşen dosyayı karşılaştırın ve güncelleyin.
- İlgisiz local değişiklikleri geri almayın.
