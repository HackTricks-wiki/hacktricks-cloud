# Permission risk categorizations

HackTricks Cloud, [CloudPEASS](https://github.com/peass-ng/CloudPEASS) ve [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) tarafından kullanılan paylaşılan permission severity verilerini tutar. Oluşturulan kopyalar yerine buradaki canonical platform dosyasını düzenleyin.

- **Critical**: Doğrudan veya neredeyse bağımsız olarak güçlü ayrıcalıklar veren, bir identity oluşturan ya da ayrıcalıklı execution sağlayan permission'lar.
- **High**: Hassas bilgilere veya credentials'a erişim ya da koşullu bir privilege escalation yolu.
- **Medium**: DoS/Break, operasyonel kesinti, olağan değişiklikler veya gösterilmiş bir hassas veri ya da ayrıcalık yolu olmayan koşullu yetenekler.
- **Low**: Olağan discovery ve metadata erişimi.

Her platform için bir canonical YAML dosyası vardır: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) ve [Kubernetes](k8s.yaml). Bunlar machine-readable dosyalardır; platform sayfaları bunların nasıl düzenleneceğini açıklar.

## Cloud provider files

`version` ve `provider` schema'yı tanımlar. `permission_categories`, dört ayrı permission listesini içerir. Rating'i değiştirmek için bir permission'ı listeler arasında taşıyın. AWS ve Azure eşleştirmeleri büyük/küçük harfi yok sayar; GCP eşleştirmeleri büyük/küçük harfe duyarlıdır. Case alias'ları aynı severity içinde tekrarlanabilir, ancak çakışan rating'ler reddedilir.

`severity_overrides`, generic kurallara yönelik denetlenmiş istisnaları içerir. Bir istisna catalog'da da bulunuyorsa her iki giriş aynı olmalıdır. `severity_caps`, bir kombinasyonun seçili permission'ları yükseltmesini engeller. `non_permission_identifiers`, belgelenmiş API-method adlarını, condition key'lerini ve gerçek authorization permission'ları olmayan diğer string'leri hariç tutar.

`combinations.critical` ve `combinations.high`, permission listelerinden oluşan listelerdir: bir iç listenin her öğesi, kombinasyonun uygulanması için verilmiş olmalıdır. Kombinasyonları birlikte tutun; bunları tekil grant'lere bölmek riski olduğundan yüksek gösterir. Mevcut exact ve regular-expression alanları, catalog'da bulunmayan permission'lar için fallback olarak kalır. Tam bir classifier rewrite veya yeni matching behavior, consumer'larda hâlâ code değişiklikleri gerektirir.

## Kubernetes file

`rules` sıralıdır: ilk eşleşen rule kazanır. Her rule benzersiz bir `id`, bir `match`, bir `severity` ve plain-language bir `description` içerir. Daha spesifik bir rule'ı daha genel olanın önüne ekleyin veya mevcut bir rule'ın severity'sini değiştirin. Son koşulsuz fallback'i koruyun.

Eşleştirmeler composition için `all`, `any` ve `not` ya da bir `field`, `op` ve `value` karşılaştırması kullanır. Kullanılabilir alanlar `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode` ve `delegated_verb`'dir. İşlemler `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` ve (value gerektirmeyen) `truthy`'dir. `always: true` her şeyle eşleşir. Group, resource, subresource ve verb değerleri lowercase'tir. Literal wildcard, `'*'` şeklinde yazılır; bir wildcard grant'ini eşleştirmek shell pattern expansion yerine rules içinde açıkça belirtilir.

`severity_when`, eşleşen bir condition için isteğe bağlı olarak başka bir severity seçer. `severity: delegated`, constrained impersonation için ayrılmıştır: `delegated_severities` map'i delegated action'ın classification'ını conditional rating'e dönüştürür. Description placeholder'ları `{full}` ve `{verb}` gibi kullanılabilir alanlara başvurabilir. Rules veridir ve hiçbir zaman Python veya shell code olarak değerlendirilmez.

## Validation and synchronization

Değişiklikleri göndermeden önce PyYAML kurulu olarak `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` komutunu çalıştırın. Book'un pull-request workflow'su aynı validation'ı çalıştırır.

Her pazartesi, her iki consumer repository de bu book'un güncel `master`'ını checkout eder, dört dosyanın tamamını validate eder, SHA-256 hash'lerini karşılaştırır ve bundled YAML dosyaları ile generated legacy list'lerini günceller. Bir source manifest, book revision'ını ve her dosyanın hash'ini kaydeder. Book'taki ilgisiz değişiklikler hiçbir consumer commit'i oluşturmaz. Her workflow manual run'ı da destekler. Tests, workflow değişen verileri consumer'ın default branch'ine commit etmeden önce çalışır; başarısızlıklar bu branch'i değiştirmeden bırakır. Consumer'lar güncellemeler arasında offline olarak bundled kopyalarını kullanmaya devam eder.

Bir consumer'da local olarak güncellemek için `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` komutunu çalıştırın. Kopyaların güncel olmadığını yazma işlemi yapmadan tespit etmek için `--check` ekleyin.
