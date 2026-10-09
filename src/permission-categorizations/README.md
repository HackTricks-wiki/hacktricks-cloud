# Permission जोखिम वर्गीकरण

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud, [CloudPEASS](https://github.com/peass-ng/CloudPEASS) और [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) द्वारा उपयोग किए जाने वाले साझा permission severity डेटा का रखरखाव करता है। किसी भी consumer में बनी हुई प्रतियों के बजाय, canonical platform फ़ाइल को यहीं संपादित करें।

- **Critical**: ऐसी permissions जो सीधे, या लगभग स्वतंत्र रूप से, शक्तिशाली privileges देती हैं, कोई identity बनाती हैं, या privileged execution सक्षम करती हैं।
- **High**: संवेदनशील जानकारी या credentials तक पहुँच, या privilege escalation का कोई सशर्त रास्ता।
- **Medium**: DoS/Break, परिचालन में व्यवधान, सामान्य बदलाव, या ऐसी सशर्त क्षमताएँ जिनसे संवेदनशील डेटा या privileges तक पहुँच का कोई प्रमाणित रास्ता न हो।
- **Low**: सामान्य खोज और metadata तक पहुँच।

हर platform के लिए एक canonical YAML फ़ाइल है: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), और [Kubernetes](k8s.yaml)। ये मशीन-पठनीय फ़ाइलें हैं; platform पेज ब्राउज़र में उनका पूरा YAML दिखाते हैं और उन्हें संपादित करने का तरीका बताते हैं। इनलाइन viewer में किताब की प्रति का उपयोग होता है, जबकि PEASS workflows GitHub से canonical फ़ाइलें प्राप्त करते हैं।

## Cloud provider फ़ाइलें

`version` और `provider` schema की पहचान करते हैं। `permission_categories` में चार अलग-अलग permission सूचियाँ होती हैं। किसी permission की rating बदलने के लिए उसे एक सूची से दूसरी सूची में ले जाएँ। AWS और Azure में matching के दौरान uppercase/lowercase का अंतर अनदेखा किया जाता है; GCP में यह अंतर बना रहता है। एक ही severity के भीतर case aliases दोहराए जा सकते हैं, लेकिन परस्पर विरोधी ratings अस्वीकार की जाती हैं।

`severity_overrides` में generic rules के लिए ऑडिट किए गए अपवाद होते हैं। अगर कोई अपवाद catalog में भी मौजूद है, तो दोनों प्रविष्टियों की rating एक जैसी होनी चाहिए। `severity_caps` किसी combination को चुनी हुई permissions का दर्जा बढ़ाने से रोकता है। `non_permission_identifiers` में दस्तावेज़ीकृत API-method नाम, condition keys और ऐसी अन्य strings शामिल नहीं होतीं जो वास्तविक authorization permissions नहीं हैं।

`combinations.critical` और `combinations.high` में permission सूचियों की सूचियाँ होती हैं: किसी combination के लागू होने के लिए भीतरी सूची के हर तत्व का grant होना ज़रूरी है। Combinations को साथ रखें; उन्हें अलग-अलग grants में बाँटने से जोखिम बढ़ा-चढ़ाकर आँका जाएगा। Catalog में मौजूद न होने वाली permissions के लिए, मौजूदा exact और regular-expression fields fallback के रूप में काम करते हैं। Classifier को पूरी तरह दोबारा लिखने या नया matching behavior जोड़ने के लिए consumers में code changes करना अब भी ज़रूरी है।

## Kubernetes फ़ाइल

`rules` क्रम में होती हैं: सबसे पहले match होने वाला rule लागू होता है। हर rule का एक विशिष्ट `id`, एक `match`, एक `severity`, और सादे भाषा में लिखा `description` होता है। किसी व्यापक rule से पहले अधिक विशिष्ट rule जोड़ें, या किसी मौजूदा rule की severity बदलें। आख़िरी unconditional fallback को जस का तस रखें।

Composition के लिए matches में `all`, `any`, और `not` का उपयोग करें, या `field`, `op`, और `value` की तुलना करें। उपलब्ध fields हैं: `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode`, और `delegated_verb`। Operations हैं: `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, और `truthy` (इसके लिए value की आवश्यकता नहीं है)। `always: true` हर चीज़ से match करता है। Group, resource, subresource, और verb की values lowercase होती हैं। Literal wildcard को `'*'` के रूप में लिखा जाता है; wildcard grant से matching rules में स्पष्ट रूप से तय होती है, shell pattern expansion के ज़रिए नहीं।

`severity_when` किसी match करने वाली condition के लिए वैकल्पिक रूप से दूसरी severity चुनता है। `severity: delegated` केवल constrained impersonation के लिए आरक्षित है: इसका `delegated_severities` map delegated action के classification को conditional rating में बदलता है। Description placeholders उपलब्ध fields का संदर्भ दे सकते हैं, जैसे `{full}` और `{verb}`। Rules डेटा हैं; उन्हें Python या shell code के रूप में कभी evaluate नहीं किया जाता।

## Validation और synchronization

बदलाव सबमिट करने से पहले, PyYAML इंस्टॉल करके `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` चलाएँ। किताब का pull-request workflow भी यही validation चलाता है।

हर सोमवार, दोनों consumer repositories इस किताब के मौजूदा `master` को checkout करती हैं, चारों फ़ाइलों को validate करती हैं, SHA-256 hashes की तुलना करती हैं, और अपने bundled YAML फ़ाइलों तथा generated legacy lists को अपडेट करती हैं। एक source manifest में किताब का revision और हर फ़ाइल का hash दर्ज होता है। किताब में असंबंधित बदलाव होने पर consumer में कोई commit नहीं होता। हर workflow को manual run भी किया जा सकता है। Workflow द्वारा बदले हुए डेटा को consumer की default branch में commit करने से पहले tests चलते हैं; विफल होने पर उस branch में कोई बदलाव नहीं होता। Updates के बीच consumers offline रहते हुए अपनी bundled copies का उपयोग करते रहते हैं।

किसी consumer में स्थानीय रूप से अपडेट करने के लिए, `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` चलाएँ। बिना फ़ाइलें लिखे पुरानी प्रतियाँ पहचानने के लिए `--check` जोड़ें।

दोनों consumers में source fetching पाँच बार retry करता है, checkout के लिए सीमित समय-सीमा और हर बार बढ़ते विलंब के साथ। अधूरे downloads अस्थायी directories में रहते हैं; सभी retries विफल होने पर मौजूदा bundled डेटा अपरिवर्तित रहता है।
{{#include ../banners/hacktricks-training.md}}
