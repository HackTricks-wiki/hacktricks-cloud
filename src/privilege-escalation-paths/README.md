# Privilege escalation yolları

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud, [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) tarafından kullanılan, makinelerce okunabilir privilege escalation kataloğunu yönetir. Her teknik, bir principal'ın hedef principal kümesindeki ayrıcalıkları elde etmek için hangi kaynaklarda hangi izinlere etkin olarak sahip olması gerektiğini belirtir. Blue-CloudPEASS bu kayıtları çevrimdışı olarak salt okunur bir envanter anlık görüntüsüne göre değerlendirir ve principal'lar arasındaki saldırı yollarını; kanıt olarak yetki veren policy veya binding'i ve yolu ortadan kaldıran azaltma önlemini göstererek çizer. Tüketicideki kopyalar yerine buradaki asıl dosyaları düzenleyin.

Kayıtlar yalnızca ön koşulları, erişilebilen hedefleri ve azaltma önlemini açıklar. Komut, payload veya yürütme adımı içermez; bağlantısı verilen HackTricks sayfası tekniği açıklar.

## Yapı

Her platform (`aws`, `gcp`, `azure`, `k8s`) için bir dizin ve her servis için tekniklerin YAML listesini içeren bir `<service>.yaml` dosyası bulunur. `_excluded*.yaml` adlı dosyalar, post-exploitation, persistence veya yapılandırmadan modellenemeyen teknikler gibi, incelenmiş ancak bilerek kayda alınmamış HackTricks tekniklerini ve bunun nedenini listeler. `privesc-technique.schema.json`, editör otomatik tamamlaması ve doğrulaması için dışa aktarılan JSON Schema'dır.

## Teknik alanları

- `id`: platform önekiyle başlayan, küresel olarak benzersiz, küçük harfli ve kebab-case biçiminde bir kimlik.
- `provider`, `service`, `title` ve `summary`: kaynağın ne elde ettiğini açıklayan tek cümle.
- `source`: bu kitaptaki tekniği belgeleyen HackTricks sayfası ve anchor; kitap kök dizinine göreli olarak belirtilir. `source_revision`, incelenen kitap commit'idir.
- `requires`: kaynağın sahip olması gereken izinler. `all_of` gerekli öğelerin tümünü, `any_of` ise alternatifleri listeler. AWS ve GCP öğelerinde `action` ve `resource`; Azure öğelerinde `action` (veya `data_action`) ve `scope`; Entra ID öğelerinde `entra_permission` veya `entra_role`; Kubernetes öğelerinde `verb`, `resource`, `subresource`, `api_group` ve `namespace` kullanılır. `{target.arn}` gibi yer tutucular bir gereksinimi hedefe bağlar.
- `target`: hedefin `kind` değeri, bir principal'a erişilebilmesi için tüm koşulları karşılaması gereken `selector` ve hedefin `scope` değeri.
- `conditions` ve `blockers`: koşul anahtarları, SCP'ler, sınırlar veya admission policy'leri gibi, yolu pratikte engelleyebilecek unsurlar.
- `confidence`, `severity`, `mitigation`, `references` ve isteğe bağlı `notes`.

Bilinmeyen alanlar, hedef türleri, selector anahtarları ve yer tutucular yok sayılmak yerine reddedilir; böylece bir kayıt hedef kümesini hiçbir zaman sessizce genişletemez veya daraltamaz. Yeni bir selector desteğini önce tüketici evaluator'ına ekleyin.

### Schema v2 birleştirmeleri

v2 loader iki yer tutucu ve bir AWS selector ekler; ayrıca mevcut K8s running-pod selector'ının GCP hedeflerinde kullanılmasına izin verir. Bu alanlar, toplanan envanterle tam eşleşme gerektirir; eksik envanter, erişilebilir bir yol yerine bilinmeyen kapsam sonucunu verir.

| Alan | Kullanımı ve gerekli biçimi |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` ve `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Bunları bir AWS `aws_account_admin` hedefinde birlikte kullanın. Her gereksinim alternatifinde bu yer tutucu üzerinde `iam:CreatePolicyVersion` bulunmalıdır. Policy, kaynağın aynı hesapta assume edebildiği bir role eklenmiş olmalıdır; evaluator policy version kapasitesini denetler ve rolün etkin izinlerini yeniden hesaplar. `SetDefaultPolicyVersion` kapsama dahil değildir. |
| `target.selector.k8s_sa_used_by_running_pod: true` | `scope: cluster` değerine sahip bir GCP `k8s_service_account` hedefinde, eşleşen GKE cluster'ında çalışan pod'lar tarafından kullanılan ve erişilebilir bir token'ı olan KSA'ları seçer. Bunu `k8s_sa_in_cluster` veya `k8s_sa_has_token_secret` ile birlikte kullanmayın. Mevcut K8s kullanımı değişmez. |
| `{source_rolebound_clusterrole}` | `api_group: rbac.authorization.k8s.io` ve `namespace: "*"` değerlerine sahip K8s `clusterroles` gereksinimlerinde `resource_name` olarak kullanın. Her alternatifte aynı ad üzerinde `escalate` ve `update` veya `patch` izinleri bulunmalıdır. Hedef, `scope: same_namespace` değerine ve `selector.k8s_sa_in_namespace: "{target.namespace}"` selector'ına sahip bir `k8s_service_account` olmalıdır; bir RoleBinding, kaynağı bu namespace'te bağlamalıdır. |

## Doğrulama ve senkronizasyon

Değişiklik göndermeden önce PyYAML kurulu olarak `python scripts/validate_privesc_paths.py --book-root .` komutunu çalıştırın. Bu komut dizin yapısını, evaluator'ın katı loader'ı (`scripts/privesc_paths_schema.py`, Blue-CloudPEASS schema modülünün bir kopyası) ile tüm kayıtları, benzersiz id'leri, kaynak sayfalarını ve başlık anchor'larını, ayrıca JSON Schema'nın güncel olup olmadığını denetler. Her iki schema dosyasını tüketiciyle bayt bayt karşılaştırmak için `--peaso-root /path/to/Blue-CloudPEASS` kullanın. Kitabın pull request workflow'u da aynı doğrulamayı çalıştırır.

Blue-CloudPEASS her pazartesi bu kitabın güncel `master` dalını checkout eder, bu dosyaları doğrular ve her dosyanın SHA-256 hash'ini önceki senkronizasyonda kaydedilen hash'lerle karşılaştırır. Upstream'de eklenen, güncellenen ve silinen dosyalar, tüketicide değiştirilmemiş kopyaların yerini alır. Her iki tarafta da değiştirilen dosyalar çakışma olarak bildirilir; teknik id'leri açıkça incelenmiş bir kayıt olmadan asla silinmez. Geçersiz içerik veya başarısız bir test, tüketicinin varsayılan dalını değiştirmez. Kitaptaki ilgisiz değişiklikler tüketicide commit oluşturmaz.
{{#include ../banners/hacktricks-training.md}}
