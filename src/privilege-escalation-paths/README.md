# Privilege escalation paths

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud, [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) द्वारा उपयोग किए जाने वाले machine-readable privilege escalation catalog का रखरखाव करता है। हर technique बताती है कि किसी principal को target principals के एक समूह के privileges पाने के लिए प्रभावी रूप से कौन-सी permissions और किन resources पर रखनी होंगी। Blue-CloudPEASS इन entries का read-only inventory snapshot पर offline मूल्यांकन करता है और principal-to-principal attack paths दिखाता है। इसमें path के प्रमाण के रूप में अनुमति देने वाली policy या binding और path को हटाने वाला mitigation शामिल होता है। Consumer में मौजूद copies के बजाय यहां की canonical files को edit करें।

Entries में केवल preconditions, reachable targets और mitigation का वर्णन होता है। इनमें कोई commands, payloads या execution steps नहीं होते; linked HackTricks page में technique की जानकारी दी गई है।

## Layout

हर platform (`aws`, `gcp`, `azure`, `k8s`) के लिए एक directory है और हर service के लिए एक `<service>.yaml` file है, जिसमें techniques की YAML list होती है। `_excluded*.yaml` नाम वाली files में उन reviewed HackTricks techniques की सूची होती है जिनकी जानबूझकर कोई entry नहीं है—जैसे post-exploitation, persistence या ऐसी techniques जिन्हें configuration से model नहीं किया जा सकता—साथ में इसका कारण भी दिया जाता है। `privesc-technique.schema.json` editor completion और validation के लिए export किया गया JSON Schema है।

## Technique fields

- `id`: globally unique, lowercase और kebab-case में, platform prefix के साथ।
- `provider`, `service`, `title` और `summary`: source को क्या मिलता है, इसका वर्णन करने वाला एक वाक्य।
- `source`: इस book के सापेक्ष, technique का दस्तावेज़ीकरण करने वाला HackTricks page और anchor। `source_revision` उस book commit को बताता है जिसे पढ़ा गया था।
- `requires`: वे permissions जो source के पास होनी चाहिए। `all_of` में हर आवश्यक item और `any_of` में विकल्प दिए जाते हैं। AWS और GCP items में `action` और `resource`, Azure items में `action` (या `data_action`) और `scope`, Entra ID items में `entra_permission` या `entra_role`, और Kubernetes items में `verb`, `resource`, `subresource`, `api_group` और `namespace` का उपयोग होता है। `{target.arn}` जैसे placeholders किसी requirement को target से जोड़ते हैं।
- `target`: target का `kind`, एक `selector` जिसकी सभी शर्तें पूरी होनी चाहिए ताकि principal तक पहुंचा जा सके, और उसका `scope`।
- `conditions` और `blockers`: वे चीज़ें जो व्यवहार में path को रोक सकती हैं, जैसे condition keys, SCPs, boundaries या admission policies।
- `confidence`, `severity`, `mitigation`, `references` और वैकल्पिक `notes`।

अज्ञात fields, target kinds, selector keys और placeholders को अनदेखा करने के बजाय अस्वीकार किया जाता है, ताकि कोई entry चुपचाप अपने target set को कभी विस्तृत या सीमित न कर सके। नया selector जोड़ने के लिए पहले consumer evaluator में उसका support जोड़ें।

## Validation and synchronization

बदलाव सबमिट करने से पहले PyYAML इंस्टॉल करके `python scripts/validate_privesc_paths.py --book-root .` चलाएं। यह directory layout, evaluator के strict loader (`scripts/privesc_paths_schema.py`, Blue-CloudPEASS schema module की एक copy) से हर entry, unique ids, इस book में हर `source` page की मौजूदगी और JSON Schema के current होने की जांच करता है। Book का pull-request workflow भी यही validation चलाता है।

हर सोमवार, Blue-CloudPEASS इस book के current `master` को checkout करता है, इन files को validate करता है और हर file के SHA-256 hash की तुलना पिछले synchronization में दर्ज hashes से करता है। Upstream में जोड़ी, अपडेट या हटाई गई entries, consumer की unchanged copies की जगह लेती हैं। दोनों ओर बदली गई file को conflict के रूप में रिपोर्ट किया जाता है, और स्पष्ट रूप से reviewed ledger के बिना technique ids कभी हटाई नहीं जातीं। Invalid content या failed test होने पर consumer की default branch अपरिवर्तित रहती है। Book में असंबंधित बदलावों से consumer में कोई commit नहीं बनता।

{{#include ../banners/hacktricks-training.md}}
