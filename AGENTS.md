# AGENTS.md

Bu depoda gelecekte çalışacak agent'lar için yönergeler.

## Repository Context

Bu, HackTricks Cloud mdBook deposudur. İlgili ana kitap şu konumda bulunur:

`/Users/carlospolop/git/hacktricks`

Paylaşılan tema/search davranışında yapılan değişikliklerin genellikle her iki depoya da uygulanması gerekir.

## Search Index Loading Contract

Özel search arayüzü şu konumda bulunur:

`theme/ht_searcher.js`

Ayrıca şu konumda oluşturulmuş bir kopya da bulunabilir:

`book/theme/ht_searcher.js`

Production, önceden oluşturulmuş `book/` dizinini deploy ediyorsa her iki kopyayı da güncelleyin veya kitabı yeniden oluşturun.

Search index yükleme sırası önemlidir ve maliyete duyarlıdır:

1. GitHub repository'sinden tüm dile özgü ve fallback search index'lerini yükleyin:
`HackTricks-wiki/hacktricks-searchindex`
2. Yalnızca GitHub üzerinde barındırılan tüm adaylar başarısız olursa aynı-origin mdBook çıktısına fallback yapın.

Yerel `/searchindex.js` fallback'ini, `searchindex-cloud-en.js.gz` gibi GitHub üzerinde barındırılan herhangi bir fallback'in önüne koymayın. Production'da `cloud.hacktricks.wiki` üzerinden `searchindex.js` sunmak maliyetlidir.

Bu repo için beklenen yerel fallback:

`/searchindex.js`

Bu repo için ana-book fallback'i:

`/searchindex-book.js`

Bu dosya yalnızca fallback'tir. Birincil kaynak, `HackTricks-wiki/hacktricks-searchindex` içindeki uzak
`searchindex-<lang>.js.gz` ve `searchindex-cloud-<lang>.js.gz` dosyaları olarak kalmalıdır.

## Search Index Publishing

Şifrelenmiş sıkıştırılmış search index'lerini `HackTricks-wiki/hacktricks-searchindex` adresine publish eden workflow'lar şunlardır:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Oluşturulan kaynak dosya `book/searchindex.js` dosyasıdır. Publish edilen uzak artifact adları şunlardır:

- `searchindex-cloud-v2-en.json.gz` (tercih edilen compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (tercih edilen compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader, compact v2 artifact'ini tercih eder ve `.js.gz` artifact'ini legacy fallback olarak korur. Her ikisi de `theme/ht_searcher.js` içinde tanımlanan key kullanılarak XOR ile şifrelenmiş gzip payload'larıdır.

## Build And Validation

Yaygın yerel kontroller:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` başarısız olursa şunları kontrol edin:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Arama yapmak için `rg` kullanmayı tercih edin.
- Açıkça istenmediği sürece oluşturulan `book/` çıktısını commit'lere dahil etmeyin. Zaten oluşturulmuş sayfaların hemen düzeltilmesi gerektiğinde search loader düzeltmeleri istisnadır.
- Paylaşılan tema davranışını değiştiriyorsanız `/Users/carlospolop/git/hacktricks` içindeki eşleşen dosyayı karşılaştırın ve güncelleyin.
- İlgisiz yerel değişiklikleri geri almayın.
