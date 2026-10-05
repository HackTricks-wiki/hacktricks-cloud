# Permission risk categorizations

HackTricks Cloud, [CloudPEASS](https://github.com/peass-ng/CloudPEASS) ve [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) tarafından kullanılan paylaşılan permission severity verilerini tutar. Her iki consumer'daki oluşturulmuş kopyalar yerine buradaki canonical platform dosyasını düzenleyin.

- **Critical**: doğrudan veya neredeyse bağımsız olarak güçlü ayrıcalıklar sağlayan, bir identity oluşturan ya da privileged execution sağlayan permission'lar.
- **High**: hassas bilgilere veya credential'lara erişim ya da koşullu bir privilege escalation yolu.
- **Medium**: DoS/Break, operasyonel kesinti, olağan değişiklikler veya hassas veri ya da privilege yolu gösterilmemiş koşullu yetenekler.
- **Low**: olağan discovery ve metadata erişimi.

Her platform için bir canonical YAML dosyası vardır: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) ve [Kubernetes](k8s.yaml). Bunlar machine-readable dosyalardır; platform sayfaları tarayıcıda YAML'ın tamamını görüntüler ve nasıl düzenleneceğini açıklar. Inline viewer kitabın kopyasını kullanırken PEASS workflow'ları canonical dosyaları GitHub'dan çeker.

## Cloud provider files

`version` ve `provider` schema'yı tanımlar. `permission_categories`, dört ayrı permission listesini içerir. Rating'i değiştirmek için bir permission'ı listeler arasında taşıyın. AWS ve Azure eşleştirmelerinde büyük/küçük harf dikkate alınmaz; GCP eşleştirmelerinde büyük/küçük harf korunur. Aynı severity içinde case alias'ları tekrarlanabilir, ancak çakışan rating'ler reddedilir.

`severity_overrides`, generic kurallara yönelik denetlenmiş istisnaları içerir. Bir istisna catalog'da da yer alıyorsa her iki giriş aynı olmalıdır. `severity_caps`, bir combination'ın seçili permission'ları yükseltmesini engeller. `non_permission_identifiers`, belgelenmiş API-method adlarını, condition key'lerini ve gerçek authorization permission'ları olmayan diğer string'leri hariç tutar.

`combinations.critical` ve `combinations.high`, permission listelerinden oluşan listelerdir: bir iç listenin her öğesi, combination'ın uygulanması için verilmiş olmalıdır. Combination'ları birlikte tutun; bunları ayrı grant'lere bölmek riski olduğundan yüksek gösterir. Catalog'da bulunmayan permission'lar için mevcut exact ve regular-expression alanları fallback olarak kalır. Classifier'ın tamamen yeniden yazılması veya yeni matching davranışı, consumer'larda hâlâ code değişiklikleri gerektirir.

## Kubernetes file

`rules` sıralıdır: ilk eşleşen rule kazanır. Her rule benzersiz bir `id`, bir `match`, bir `severity` ve plain-language bir `description` içerir. Daha specific bir rule'ı daha geniş bir rule'ın önüne ekleyin veya mevcut bir rule'ın severity'sini değiştirin. Son unconditional fallback'i koruyun.

Match'ler composition için `all`, `any` ve `not` kullanır veya bir `field`, `op` ve `value` karşılaştırması kullanır. Kullanılabilir field'lar `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode` ve `delegated_verb`'dir. Operations değerleri `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` ve (value gerektirmeyen) `truthy`'dir. `always: true` her şeyle eşleşir. Group, resource, subresource ve verb değerleri lowercase'tir. Literal wildcard `'*'` şeklinde yazılır; bir wildcard grant'ini eşleştirmek, shell pattern expansion yerine rule'larda açıkça belirtilir.

`severity_when`, eşleşen bir condition için isteğe bağlı olarak başka bir severity seçer. `severity: delegated`, constrained impersonation için ayrılmıştır: `delegated_severities` map'i delegated action'ın classification'ını conditional rating'e dönüştürür. Description placeholder'ları `{full}` ve `{verb}` gibi kullanılabilir field'lara başvurabilir. Rule'lar data'dır ve hiçbir zaman Python veya shell code olarak değerlendirilmez.

## Validation and synchronization

Değişiklikleri göndermeden önce PyYAML kurulu olarak `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` komutunu çalıştırın. Kitabın pull-request workflow'u aynı validation'ı çalıştırır.

Her pazartesi, her iki consumer repository de bu kitabın güncel `master` branch'ini checkout eder, dört dosyanın tamamını validate eder, SHA-256 hash'lerini karşılaştırır ve kendi bundled YAML dosyalarını ve oluşturulmuş legacy listelerini günceller. Bir source manifest, book revision'ını ve her dosyanın hash'ini kaydeder. Kitaptaki ilgisiz değişiklikler consumer commit'i oluşturmaz. Her workflow manual run'i de destekler. Workflow, değişen verileri consumer'ın default branch'ine commit etmeden önce testleri çalıştırır; başarısızlıklar bu branch'i değiştirmeden bırakır. Güncellemeler arasında consumer'lar offline olarak bundled kopyalarını kullanmaya devam eder.

Bir consumer'da yerel olarak güncelleme yapmak için `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` komutunu çalıştırın. Yazma işlemi yapmadan eski kopyaları tespit etmek için `--check` ekleyin.

Her iki consumer'daki source fetching, beş kez retry eder; checkout deadline'ları sınırlandırılmıştır ve beklemeler giderek artırılır. Tamamlanmamış indirmeler temporary directory'lerde tutulur; retry'lar tükendiğinde mevcut bundled data değiştirilmeden bırakılır.
