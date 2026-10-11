# Privilege escalation paths

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud, [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) tarafından kullanılan, makine tarafından okunabilir privilege escalation kataloğunu tutar. Her teknik, bir principal'ın hedef principal'lardan oluşan bir kümenin ayrıcalıklarını elde etmek için hangi kaynaklarda hangi izinlere etkin biçimde sahip olması gerektiğini belirtir. Blue-CloudPEASS bu girdileri salt okunur bir envanter snapshot'ına karşı çevrimdışı değerlendirir ve kanıt olarak izin veren policy veya binding'i, yolu kaldıran mitigation ile birlikte göstererek principal'lar arasındaki saldırı yollarını çizer. Tüketicideki kopyaları değil, buradaki canonical dosyaları düzenleyin.

Girdiler yalnızca ön koşulları, erişilebilir hedefleri ve mitigation'ı açıklar. Komut, payload veya yürütme adımı içermez; bağlantılı HackTricks sayfası tekniği açıklar.

## Layout

Her platform için (`aws`, `gcp`, `azure`, `k8s`) bir dizin ve her servis için tekniklerin YAML listesini içeren bir `<service>.yaml` dosyası bulunur. `_excluded*.yaml` adlı dosyalar, nedenleriyle birlikte, post-exploitation, persistence veya yapılandırmadan modellenemeyen teknikler gibi bilinçli olarak girdisi bulunmayan ve gözden geçirilmiş HackTricks tekniklerini listeler. `privesc-technique.schema.json`, editör otomatik tamamlama ve doğrulaması için dışa aktarılmış JSON Schema'dır.

## Technique fields

- `id`: platform önekiyle başlayan, global olarak benzersiz, küçük harfli ve kebab-case bir kimlik.
- `provider`, `service`, `title` ve `summary`: kaynağın ne elde ettiğini açıklayan tek cümle.
- `source`: bu kitaba göreli olarak, tekniği belgeleyen HackTricks sayfası ve anchor. `source_revision`, okunan kitap commit'idir.
- `requires`: kaynağın sahip olması gereken izinler. `all_of` gerekli tüm öğeleri, `any_of` ise alternatifleri listeler. AWS ve GCP öğeleri `action` ve `resource`; Azure öğeleri `action` (veya `data_action`) ve `scope`; Entra ID öğeleri `entra_permission` veya `entra_role`; Kubernetes öğeleri ise `verb`, `resource`, `subresource`, `api_group` ve `namespace` kullanır. `{target.arn}` gibi placeholder'lar bir gereksinimi hedefe bağlar.
- `target`: hedefin `kind` değerini, bir principal'ın erişilebilir olması için koşullarının tümü sağlanması gereken `selector`'ı ve `scope` değerini belirtir.
- `conditions` ve `blockers`: koşul anahtarları, SCP'ler, sınırlar veya admission policy'ler gibi, uygulamada yolu engelleyebilecek unsurları belirtir.
- `confidence`, `severity`, `mitigation`, `references` ve isteğe bağlı `notes`.

Bilinmeyen alanlar, hedef türleri, selector anahtarları ve placeholder'lar yok sayılmak yerine reddedilir; böylece bir girdi hedef kümesini sessizce genişletemez veya daraltamaz. Yeni bir selector için önce tüketici evaluator'ına destek ekleyin.

## Validation and synchronization

Değişiklikleri göndermeden önce PyYAML yüklüyken `python scripts/validate_privesc_paths.py --book-root .` komutunu çalıştırın. Bu komut dizin düzenini, evaluator'ın katı loader'ı (`scripts/privesc_paths_schema.py`, Blue-CloudPEASS schema modülünün bir kopyası) ile her girdiyi, benzersiz kimlikleri, her `source` sayfasının bu kitapta mevcut olduğunu ve JSON Schema'nın güncel olduğunu denetler. Kitabın pull-request workflow'u da aynı doğrulamayı çalıştırır.

Her pazartesi Blue-CloudPEASS bu kitabın güncel `master` dalını checkout eder, bu dosyaları doğrular ve her dosyanın SHA-256 hash'ini önceki senkronizasyon sırasında kaydedilen hash'lerle karşılaştırır. Upstream eklemeleri, güncellemeleri ve silmeleri, değiştirilmemiş tüketici kopyalarının üzerine yazar. Her iki tarafta da değiştirilmiş bir dosya çakışma olarak bildirilir ve açıkça incelenmiş bir ledger olmadan teknik kimlikleri hiçbir zaman silinmez. Geçersiz içerik veya başarısız bir test, tüketicinin varsayılan dalını değiştirmez. Kitaptaki ilgisiz değişiklikler tüketici tarafında commit oluşturmaz.

{{#include ../banners/hacktricks-training.md}}
