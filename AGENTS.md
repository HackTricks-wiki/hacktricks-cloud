# AGENTS.md

Gelecekte bu depoda çalışan ajanlar için rehber.

## Repository Bağlamı

Bu, HackTricks Cloud mdBook reposudur. İlgili ana kitap şurada bulunur:

`/Users/carlospolop/git/hacktricks`

Paylaşılan theme/search davranışındaki değişikliklerin genellikle her iki repoda da uygulanması gerekir.

## Search Index Yükleme Sözleşmesi

Özel arama UI'sı şurada bulunur:

`theme/ht_searcher.js`

Ayrıca oluşturulmuş bir kopya da olabilir:

`book/theme/ht_searcher.js`

Eğer production zaten oluşturulmuş `book/` dizinini deploy ediyorsa, her iki kopyayı da güncelleyin veya deploydan önce
book'u yeniden build edin.

Search index yükleme sırası önemlidir ve maliyet açısından kritiktir:

1. GitHub repository'sinden her dil-özgü ve fallback search index'i yükle:
`HackTricks-wiki/hacktricks-searchindex`
2. Sadece tüm GitHub-hosted adaylar başarısız olursa, aynı-origin mdBook çıktısına fallback yap.

Yerel `/searchindex.js` fallback'ini, `searchindex-cloud-en.js.gz` gibi herhangi bir GitHub-hosted fallback'ten önce koymayın. Production'da `cloud.hacktricks.wiki` üzerinden `searchindex.js` servis etmek pahalıdır.

Bu repo için beklenen yerel fallback şudur:

`/searchindex.js`

Ana kitap için bu repodaki fallback şudur:

`/searchindex-book.js`

Bu dosya yalnızca bir fallback'tir. Birincil kaynak, `HackTricks-wiki/hacktricks-searchindex` içindeki remote
`searchindex-<lang>.js.gz` ve `searchindex-cloud-<lang>.js.gz` dosyaları olarak kalmalıdır.

## Search Index Yayınlama

Şifrelenmiş sıkıştırılmış search index'leri `HackTricks-wiki/hacktricks-searchindex` içine yayınlayan workflow'lar şunlardır:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Oluşturulan kaynak dosya `book/searchindex.js`'dir. Yayınlanan remote artifact adları şunlardır:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Tarayıcı loader, `theme/ht_searcher.js` içinde tanımlı anahtarı kullanan XOR-şifrelenmiş gzip payload'ları olan remote `.js.gz` dosyalarını bekler.

## Build Ve Validation

Yaygın yerel kontroller:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` başarısız olursa, şunları kontrol edin:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notları

- Arama için `rg` kullanmayı tercih edin.
- Özellikle istenmedikçe oluşturulmuş `book/` çıktısını commitlere dahil etmeyin. Search loader düzeltmeleri, zaten oluşturulmuş sayfaların hemen düzeltilmesi gerektiğinde istisnadır.
- Paylaşılan theme davranışını değiştiriyorsanız, `/Users/carlospolop/git/hacktricks` içindeki eşleşen dosyayı karşılaştırın ve güncelleyin.
- İlgisiz yerel değişiklikleri geri almayın.
