# Privilege escalation paths

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud, [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) द्वारा उपयोग की जाने वाली machine-readable privilege escalation catalog का रखरखाव करता है। हर technique बताती है कि किसी principal को target principals के एक समूह के privileges पाने के लिए कौन-सी permissions प्रभावी रूप से और किन resources पर रखनी होंगी। Blue-CloudPEASS read-only inventory snapshot पर इन entries का offline मूल्यांकन करता है और principal-to-principal attack paths दिखाता है। इसमें granting policy या binding को evidence के रूप में और path हटाने वाले mitigation को भी दिखाया जाता है। Consumer में मौजूद copies के बजाय यहां canonical files में बदलाव करें।

Entries में केवल preconditions, पहुंच में आने वाले targets और mitigation का वर्णन होता है। इनमें कोई commands, payloads या execution steps नहीं होते; linked HackTricks page में technique की व्याख्या है।

## Layout

हर platform (`aws`, `gcp`, `azure`, `k8s`) के लिए एक directory है और हर service के लिए एक `<service>.yaml` file है, जिसमें techniques की YAML list होती है। `_excluded*.yaml` नाम वाली files में उन HackTricks techniques की सूची होती है जिनकी समीक्षा की गई है, लेकिन जानबूझकर कोई entry नहीं बनाई गई है—जैसे post-exploitation, persistence या ऐसी techniques जिन्हें configuration से model नहीं किया जा सकता। इनमें ऐसा करने का कारण भी दिया जाता है। `privesc-technique.schema.json` editor completion और validation के लिए exported JSON Schema है।

## Technique fields

- `id`: globally unique, lowercase और kebab-case में, जिसकी शुरुआत platform के नाम से होती है।
- `provider`, `service`, `title` और `summary`: एक वाक्य में बताएं कि source को क्या मिलता है।
- `source`: इस technique को दर्ज करने वाला HackTricks page और anchor, जो इस book के सापेक्ष दिया जाता है। `source_revision` उस book commit को बताता है जिसे पढ़ा गया था।
- `requires`: source के पास होनी आवश्यक permissions। `all_of` में सभी आवश्यक items और `any_of` में विकल्प दिए जाते हैं। AWS और GCP items में `action` और `resource`, Azure items में `action` (या `data_action`) और `scope`, Entra ID items में `entra_permission` या `entra_role`, और Kubernetes items में `verb`, `resource`, `subresource`, `api_group` और `namespace` इस्तेमाल होते हैं। `{target.arn}` जैसे placeholders किसी requirement को target से जोड़ते हैं।
- `target`: target का `kind`, एक `selector` जिसकी सभी शर्तें किसी principal को reachable बनाने के लिए पूरी होनी चाहिए, और उसका `scope`।
- `conditions` और `blockers`: वे चीजें जो वास्तविक स्थिति में path को रोक सकती हैं, जैसे condition keys, SCPs, boundaries या admission policies।
- `confidence`, `severity`, `mitigation`, `references` और वैकल्पिक `notes`।

अज्ञात fields, target kinds, selector keys और placeholders को अनदेखा करने के बजाय अस्वीकार किया जाता है, ताकि कोई entry चुपचाप अपने target set को बड़ा या छोटा न कर सके। नया selector जोड़ने से पहले consumer evaluator में उसका support जोड़ें।

### Schema v2 joins

v2 loader में दो placeholders और एक AWS selector जोड़े गए हैं, और मौजूदा K8s running-pod selector को GCP targets पर इस्तेमाल करने की अनुमति दी गई है। इन fields के लिए collected inventory से exact join आवश्यक है; inventory न मिलने पर coverage अज्ञात माना जाता है, reachable path नहीं।

| Field | उपयोग और आवश्यक shape |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` और `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | इन्हें AWS `aws_account_admin` target पर साथ इस्तेमाल करें। हर requirement alternative में उस placeholder पर `iam:CreatePolicyVersion` शामिल होना चाहिए। Policy उसी account में उस role से attached होनी चाहिए जिसे source assume कर सकता है; evaluator policy version की capacity जांचता है और role की effective permissions फिर से गणना करता है। `SetDefaultPolicyVersion` शामिल नहीं है। |
| `target.selector.k8s_sa_used_by_running_pod: true` | `scope: cluster` वाले GCP `k8s_service_account` target पर, matched GKE cluster में उपलब्ध token वाले running pods द्वारा इस्तेमाल किए जा रहे KSAs चुनता है। इसे `k8s_sa_in_cluster` या `k8s_sa_has_token_secret` के साथ न जोड़ें। मौजूदा K8s उपयोग में कोई बदलाव नहीं है। |
| `{source_rolebound_clusterrole}` | इसे K8s `clusterroles` requirements में `api_group: rbac.authorization.k8s.io` और `namespace: "*"` के साथ `resource_name` के रूप में इस्तेमाल करें। हर alternative में एक ही name पर `escalate` और `update` या `patch` होना चाहिए। Target `scope: same_namespace` वाला `k8s_service_account` होना चाहिए और उसमें `selector.k8s_sa_in_namespace: "{target.namespace}"` होना चाहिए; RoleBinding को source से उसी namespace में bind करना आवश्यक है। |

## Validation and synchronization

बदलाव जमा करने से पहले PyYAML install करके `python scripts/validate_privesc_paths.py --book-root .` चलाएं। यह directory layout, evaluator के strict loader (`scripts/privesc_paths_schema.py`, Blue-CloudPEASS schema module की एक copy) से हर entry, unique ids, source pages और heading anchors, तथा JSON Schema के current होने की जांच करता है। दोनों schema files की consumer से byte-for-byte तुलना करने के लिए `--peaso-root /path/to/Blue-CloudPEASS` इस्तेमाल करें। Book का pull-request workflow भी यही validation चलाता है।

हर सोमवार, Blue-CloudPEASS इस book के मौजूदा `master` को checkout करता है, इन files को validate करता है और हर file के SHA-256 hash की तुलना पिछले synchronization में दर्ज hashes से करता है। Upstream में जोड़ी गई, अपडेट की गई और हटाई गई files से consumer की unchanged copies बदल दी जाती हैं। दोनों तरफ बदली गई file को conflict के रूप में रिपोर्ट किया जाता है, और बिना स्पष्ट रूप से review किए गए ledger के technique ids कभी नहीं हटाए जाते। Invalid content या असफल test होने पर consumer की default branch में कोई बदलाव नहीं होता। Book में असंबंधित बदलावों से consumer में कोई commit नहीं बनता।
{{#include ../banners/hacktricks-training.md}}
