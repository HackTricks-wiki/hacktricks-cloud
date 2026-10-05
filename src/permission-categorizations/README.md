# Permission risk categorizations

HackTricks Cloud, [CloudPEASS](https://github.com/peass-ng/CloudPEASS) और [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS द्वारा उपयोग किए जाने वाले साझा permission severity data को बनाए रखता है। दोनों consumers में मौजूद generated copies के बजाय यहां canonical platform file को edit करें।

- **Critical**: ऐसी permissions जो सीधे या लगभग स्वतंत्र रूप से powerful privileges प्रदान करती हैं, identity बनाती हैं या privileged execution सक्षम करती हैं।
- **High**: sensitive information, credentials या conditional privilege escalation path तक access।
- **Medium**: DoS/Break, operational disruption, सामान्य changes या ऐसी conditional capabilities जिनके लिए sensitive-data या privilege path प्रदर्शित नहीं किया गया है।
- **Low**: सामान्य discovery और metadata access।

प्रत्येक platform के लिए एक canonical YAML file है: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) और [Kubernetes](k8s.yaml)। ये machine-readable files हैं; platform pages browser में उनका पूरा YAML प्रदर्शित करते हैं और उन्हें edit करने का तरीका बताते हैं। Inline viewer book की copy का उपयोग करता है, जबकि PEASS workflows GitHub से canonical files fetch करते हैं।

## Cloud provider files

`version` और `provider` schema की पहचान करते हैं। `permission_categories` में चार individual permission lists होती हैं। किसी permission को एक list से दूसरी list में ले जाकर उसकी rating बदलें। AWS और Azure matching में case को ignore किया जाता है; GCP matching में case सुरक्षित रहता है। Case aliases एक ही severity में दोहराए जा सकते हैं, लेकिन conflicting ratings अस्वीकार की जाती हैं।

`severity_overrides` में generic rules के audited exceptions होते हैं। यदि कोई exception catalog में भी दिखाई देता है, तो दोनों entries का सहमत होना आवश्यक है। `severity_caps` किसी combination को चुनी गई permissions को upgrade करने से रोकता है। `non_permission_identifiers` documented API-method names, condition keys और अन्य ऐसे strings को बाहर रखता है जो वास्तविक authorization permissions नहीं हैं।

`combinations.critical` और `combinations.high` permission lists की सूचियां हैं: combination लागू होने के लिए inner list के प्रत्येक element का granted होना आवश्यक है। Combinations को साथ रखें; उन्हें individual grants में विभाजित करने से risk बढ़ा-चढ़ाकर प्रदर्शित होगा। Catalog में अनुपस्थित permissions के लिए मौजूदा exact और regular-expression fields fallback के रूप में बने रहते हैं। पूर्ण classifier rewrite या नया matching behavior अभी भी consumers में code changes की मांग करता है।

## Kubernetes file

`rules` ordered होती हैं: पहली matching rule लागू होती है। प्रत्येक rule में एक unique `id`, एक `match`, एक `severity` और plain-language `description` होती है। अधिक specific rule को broader rule से पहले जोड़ें या किसी मौजूदा rule की severity बदलें। अंतिम unconditional fallback को सुरक्षित रखें।

Matches composition के लिए `all`, `any` और `not` या `field`, `op` और `value` comparison का उपयोग करते हैं। उपलब्ध fields हैं: `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode` और `delegated_verb`। Operations हैं `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` और `truthy` (किसी value की आवश्यकता नहीं)। `always: true` हर चीज़ से match करता है। Group, resource, subresource और verb values lowercase होती हैं। Literal wildcard को `'*'` के रूप में लिखा जाता है; wildcard grant से matching rules में explicit होती है, shell pattern expansion के रूप में नहीं।

`severity_when` matching condition के लिए वैकल्पिक रूप से दूसरी severity चुनता है। `severity: delegated` constrained impersonation के लिए reserved है: इसका `delegated_severities` map delegated action के classification को conditional rating में बदलता है। Description placeholders उपलब्ध fields, जैसे `{full}` और `{verb}`, का reference दे सकते हैं। Rules data होती हैं और इन्हें कभी Python या shell code के रूप में evaluate नहीं किया जाता।

## Validation and synchronization

Changes submit करने से पहले PyYAML installed होने पर `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` चलाएं। Book का pull-request workflow यही validation चलाता है।

प्रत्येक सोमवार, दोनों consumer repositories इस book के वर्तमान `master` को checkout करते हैं, सभी चार files को validate करते हैं, SHA-256 hashes की तुलना करते हैं और अपनी bundled YAML files तथा generated legacy lists को update करते हैं। Source manifest में book revision और प्रत्येक file का hash दर्ज होता है। Book में unrelated changes से कोई consumer commit नहीं बनता। प्रत्येक workflow manual run का भी समर्थन करता है। Workflow द्वारा consumer की default branch में changed data commit करने से पहले tests चलते हैं; failures होने पर वह branch अपरिवर्तित रहती है। Updates के बीच consumers offline रहते हुए अपनी bundled copies का उपयोग करते हैं।

किसी consumer में locally update करने के लिए `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` चलाएं। Copies को लिखे बिना stale copies का पता लगाने के लिए `--check` जोड़ें।

दोनों consumers में source fetching bounded checkout deadlines और बढ़ते delays के साथ पांच बार retry करता है। Incomplete downloads temporary directories में रहते हैं; retries समाप्त होने पर मौजूदा bundled data अपरिवर्तित रहता है।
