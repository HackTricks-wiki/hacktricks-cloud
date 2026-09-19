# AGENTS.md

Bu repository üzerinde çalışan gelecekteki agent'lar için rehber.

## Repository Context

Bu, HackTricks Cloud mdBook repository'sidir. İlgili ana kitap şu konumda bulunur:

`/Users/carlospolop/git/hacktricks`

Paylaşılan theme/search davranışındaki değişikliklerin çoğu zaman her iki repository'ye de uygulanması gerekir.

## Search Index Loading Contract

Özel search UI şu dosyada bulunur:

`theme/ht_searcher.js`

Ayrıca oluşturulmuş bir kopya şu konumda bulunabilir:

`book/theme/ht_searcher.js`

Production zaten oluşturulmuş `book/` directory'sini deploy ediyorsa her iki kopyayı da güncelleyin veya book'u yeniden oluşturun.

Search index source policy önemlidir ve maliyete duyarlıdır:

- Public host'larda her language-specific ve fallback candidate'ı yalnızca
`HackTricks-wiki/hacktricks-searchindex` üzerinden yükleyin. Aynı-origin mdBook output'una kesinlikle fallback yapmayın; production'da büyük index'i `cloud.hacktricks.wiki` üzerinden sunmak pahalıdır.
- Localhost, `.local`/`.internal` host'larda, loopback, RFC1918, carrier-grade NAT, link-local veya private IPv6 address'lerinde yalnızca aynı-origin mdBook output'unu yükleyin; böylece local/container deployment'lar self-contained kalır. English olmayan bir page için önce language-prefixed local path'i deneyin (örneğin `/es/searchindex.js`) ve yalnızca fallback olarak root English index'ini kullanın.

Bu repo için beklenen local fallback:

`/searchindex.js`

Bu repo için ana-book fallback'i:

`/searchindex-book.js`

Bu local file'lar yalnızca private-network source'larıdır. Public host'lar yalnızca
`HackTricks-wiki/hacktricks-searchindex` içindeki remote
`searchindex-<lang>.js.gz` ve `searchindex-cloud-<lang>.js.gz` file'larını kullanmalıdır.

## Search Index Publishing

Encrypted compressed search index'leri
`HackTricks-wiki/hacktricks-searchindex` repository'sine publish eden workflow'lar şunlardır:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Oluşturulan source file `book/searchindex.js`'dir. Publish edilen remote artifact adları:

- `searchindex-cloud-v2-en.json.gz` (tercih edilen compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (tercih edilen compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader, compact v2 artifact'ını tercih eder ve `.js.gz` artifact'ını legacy
fallback olarak tutar. Her ikisi de `theme/ht_searcher.js` içinde tanımlanan key kullanılarak XOR-encrypted gzip payload'larıdır.

Loader lazy kalmalıdır: normal page navigation, visitor search'ü açana veya kullanana kadar search worker'ını oluşturmamalı veya index indirmemelidir. Remote compressed response'lar origin başına 24 saat boyunca Cache Storage'da persist edilir; böylece sonraki page'ler bunları yeniden kullanabilir. Expired entry'yi refresh etmek başarısız olduğunda stale-cache fallback'ini koruyun.

## Build And Validation

Yaygın local kontroller:

- `node --check theme/ht_searcher.js`
- `mdbook build`

`mdbook build` başarısız olursa şunları kontrol edin:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Arama için `rg` kullanmayı tercih edin.
- Özellikle istenmediği sürece oluşturulan `book/` output'unu commit'lerin dışında tutun. Zaten oluşturulmuş page'lerin hemen düzeltilmesi gerektiğinde search loader düzeltmeleri istisnadır.
- Paylaşılan theme davranışını değiştiriyorsanız `/Users/carlospolop/git/hacktricks` içindeki eşleşen file'ı karşılaştırın ve güncelleyin.
- İlgisiz local değişiklikleri geri almayın.
