# İzin risk kategorileri

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud, [CloudPEASS](https://github.com/peass-ng/CloudPEASS) ve [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) tarafından kullanılan ortak izin önem derecesi verilerini yönetir. Her iki tüketicideki oluşturulmuş kopyaları değil, buradaki platformun kanonik dosyasını düzenleyin.

- **Kritik**: Doğrudan veya neredeyse bağımsız olarak güçlü ayrıcalıklar veren, bir kimlik oluşturan ya da ayrıcalıklı yürütmeye olanak tanıyan izinler.
- **Yüksek**: Hassas bilgilere veya kimlik bilgilerine erişim ya da koşullu bir ayrıcalık yükseltme yolu sağlayan izinler.
- **Orta**: DoS/Break, operasyonel aksama, sıradan değişiklikler veya kanıtlanmış bir hassas veri ya da ayrıcalık yolu olmadan koşullu yetenekler.
- **Düşük**: Sıradan keşif ve meta veri erişimi.

Her platform için bir kanonik YAML dosyası vardır: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) ve [Kubernetes](k8s.yaml). Bunlar makine tarafından okunabilen dosyalardır; platform sayfaları, YAML dosyalarının tamamını tarayıcıda gösterir ve nasıl düzenleneceklerini açıklar. Satır içi görüntüleyici kitabın kopyasını kullanırken PEASS iş akışları kanonik dosyaları GitHub'dan alır.

## Cloud sağlayıcı dosyaları

`version` ve `provider` şemayı tanımlar. `permission_categories` dört ayrı izin listesini içerir. Derecelendirmesini değiştirmek için bir izni listeler arasında taşıyın. AWS ve Azure eşleştirmelerinde büyük/küçük harf duyarlılığı yoktur; GCP eşleştirmelerinde ise büyük/küçük harf duyarlılığı korunur. Aynı önem derecesi içinde harf büyüklüğü farklı takma adlar tekrarlanabilir, ancak çelişen derecelendirmeler reddedilir.

`severity_overrides`, genel kurallara yönelik denetlenmiş istisnaları içerir. Bir istisna katalogda da yer alıyorsa her iki girdinin de aynı olması gerekir. `severity_caps`, bir birleşimin seçili izinleri daha üst bir dereceye çıkarmasını önler. `non_permission_identifiers`, belgelenmiş API yöntemi adlarını, koşul anahtarlarını ve gerçek yetkilendirme izinleri olmayan diğer dizeleri hariç tutar.

`combinations.critical` ve `combinations.high`, izin listelerinden oluşan listelerdir: bir birleşimin uygulanması için iç listelerdeki her öğenin verilmiş olması gerekir. Birleşimleri bir arada tutun; bunları tekil izinlere bölmek riski olduğundan yüksek gösterir. Mevcut tam eşleşme ve düzenli ifade alanları, katalogda bulunmayan izinler için yedek eşleştirme yöntemi olmaya devam eder. Sınıflandırıcıyı baştan yazmak veya yeni eşleştirme davranışları eklemek için tüketicilerde kod değişikliği gerekir.

## Kubernetes dosyası

`rules` sıralıdır: ilk eşleşen kural uygulanır. Her kuralın benzersiz bir `id`, bir `match`, bir `severity` ve sade dille yazılmış bir `description` alanı vardır. Daha genel bir kuraldan önce daha belirli bir kural ekleyin veya mevcut bir kuralın önem derecesini değiştirin. Son koşulsuz yedek kuralı koruyun.

Eşleşmeler; bileşim için `all`, `any` ve `not` kullanır veya `field`, `op` ve `value` karşılaştırması yapar. Kullanılabilir alanlar: `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (küçük harfli, kaynak olmayan URL), `non_resource_url`, `mode` ve `delegated_verb`. İşlemler: `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` ve `truthy` (value gerektirmez). `always: true` her şeyle eşleşir. Group, resource, subresource ve verb değerleri küçük harflidir. Gerçek bir joker karakter `'*'` olarak yazılır; joker karakter içeren bir iznin eşleştirilmesi, kabukta desen genişletmesiyle değil, kurallarda açıkça belirtilir.

`severity_when`, eşleşen bir koşul için isteğe bağlı olarak başka bir önem derecesi seçer. `severity: delegated`, kısıtlı kimliğe bürünme için ayrılmıştır: `delegated_severities` eşlemesi, devredilen eylemin sınıflandırmasını koşullu derecelendirmeye dönüştürür. Açıklama yer tutucuları, `{full}` ve `{verb}` gibi kullanılabilir alanlara başvurabilir. Kurallar veridir; Python veya kabuk kodu olarak değerlendirilmez.

## Doğrulama ve eşitleme

Değişiklikleri göndermeden önce PyYAML kurulu olacak şekilde `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` komutunu çalıştırın. Kitabın pull request iş akışı da aynı doğrulamayı çalıştırır.

Her pazartesi, her iki tüketici deposu da bu kitabın güncel `master` dalını checkout eder, dört dosyanın tümünü doğrular, SHA-256 özetlerini karşılaştırır ve paketlenmiş YAML dosyalarıyla oluşturulmuş eski listeleri günceller. Bir kaynak manifesti kitap revizyonunu ve her dosyanın özetini kaydeder. Kitaptaki ilgisiz değişiklikler tüketici depolarında commit oluşturmaz. Her iş akışı manuel olarak da çalıştırılabilir. İş akışı, değiştirilen verileri tüketicinin varsayılan dalına commit etmeden önce testleri çalıştırır; testler başarısız olursa bu dal değişmeden kalır. Tüketiciler, güncellemeler arasında çevrimdışı çalışırken paketlenmiş kopyalarını kullanmaya devam eder.

Bir tüketicide yerel olarak güncelleme yapmak için `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` komutunu çalıştırın. Kopyaların güncel olmadığını yazma işlemi yapmadan saptamak için `--check` ekleyin.

Her iki tüketicideki kaynak alma işlemi, belirli sınırlar içinde tutulan checkout zaman aşımları ve giderek artan bekleme süreleriyle beş kez yeniden denenir. Tamamlanmamış indirmeler geçici dizinlerde tutulur; tüm denemeler başarısız olursa mevcut paketlenmiş veriler değiştirilmeden kalır.
{{#include ../banners/hacktricks-training.md}}
