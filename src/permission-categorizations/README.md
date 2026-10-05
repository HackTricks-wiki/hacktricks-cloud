# Permission risk categorizations

HackTricks Cloud, [CloudPEASS](https://github.com/peass-ng/CloudPEASS) और [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) द्वारा उपयोग किए जाने वाले shared permission severity data को बनाए रखता है। दोनों consumers में मौजूद generated copies के बजाय यहां canonical platform file को edit करें।

- **Critical**: ऐसी permissions जो सीधे, या लगभग स्वतंत्र रूप से, powerful privileges प्रदान करती हैं, कोई identity mint करती हैं, या privileged execution सक्षम करती हैं।
- **High**: sensitive information, credentials, या conditional privilege escalation path तक access।
- **Medium**: DoS/Break, operational disruption, सामान्य changes, या demonstrated sensitive-data अथवा privilege path के बिना conditional capabilities।
- **Low**: सामान्य discovery और metadata access।

हर platform के लिए एक canonical YAML file है: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), और [Kubernetes](k8s.yaml)। ये machine-readable files हैं; platform pages इन्हें edit करने का तरीका समझाते हैं।

## Cloud provider files

`version` और `provider` schema की पहचान करते हैं। `permission_categories` में चार individual permission lists होती हैं। किसी permission की rating बदलने के लिए उसे एक list से दूसरी list में move करें। AWS और Azure matching में case को ignore करते हैं; GCP matching में case सुरक्षित रहता है। एक ही severity के भीतर case aliases दोहराए जा सकते हैं, लेकिन conflicting ratings अस्वीकार कर दी जाती हैं।

`severity_overrides` में generic rules के audited exceptions होते हैं। यदि कोई exception catalog में भी मौजूद है, तो दोनों entries का सहमत होना आवश्यक है। `severity_caps` किसी combination को selected permissions को upgrade करने से रोकता है। `non_permission_identifiers` documented API-method names, condition keys और अन्य ऐसे strings को बाहर रखता है जो वास्तविक authorization permissions नहीं हैं।

`combinations.critical` और `combinations.high`, permission lists की lists हैं: combination लागू होने के लिए inner list का प्रत्येक element granted होना चाहिए। Combinations को साथ रखें; उन्हें individual grants में split करने से risk बढ़ा-चढ़ाकर दिखेगा। Catalog में अनुपस्थित permissions के लिए मौजूदा exact और regular-expression fields fallback के रूप में बने रहते हैं। पूर्ण classifier rewrite या नया matching behavior अभी भी consumers में code changes की मांग करता है।

## Kubernetes file

`rules` ordered होता है: पहली matching rule लागू होती है। प्रत्येक rule में एक unique `id`, एक `match`, एक `severity`, और plain-language `description` होता है। अधिक specific rule को broader rule से पहले जोड़ें, या किसी मौजूदा rule की severity बदलें। अंतिम unconditional fallback को सुरक्षित रखें।

Composition के लिए matches में `all`, `any`, और `not` का उपयोग होता है, या `field`, `op`, और `value` comparison का। उपलब्ध fields हैं `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode`, और `delegated_verb`। Operations हैं `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, और `truthy` (किसी value की आवश्यकता नहीं)। `always: true` हर चीज़ से match करता है। Group, resource, subresource, और verb values lowercase होते हैं। Literal wildcard को `'*'` के रूप में लिखा जाता है; wildcard grant से matching rules में explicit होती है, shell pattern expansion के रूप में नहीं।

`severity_when` matching condition के लिए वैकल्पिक रूप से कोई दूसरी severity चुनता है। `severity: delegated` constrained impersonation के लिए reserved है: इसका `delegated_severities` map delegated action के classification को conditional rating में convert करता है। Description placeholders उपलब्ध fields, जैसे `{full}` और `{verb}`, को reference कर सकते हैं। Rules data होती हैं और इन्हें कभी Python या shell code के रूप में evaluate नहीं किया जाता।

## Validation and synchronization

Changes submit करने से पहले PyYAML installed होने पर `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` चलाएं। Book का pull-request workflow भी यही validation चलाता है।

हर Monday, दोनों consumer repositories इस book के वर्तमान `master` को checkout करते हैं, सभी चार files को validate करते हैं, SHA-256 hashes की तुलना करते हैं, और अपनी bundled YAML files तथा generated legacy lists को update करते हैं। एक source manifest book revision और प्रत्येक file का hash record करता है। Book में unrelated changes होने पर कोई consumer commit नहीं बनता। प्रत्येक workflow manual run को भी support करता है। Workflow द्वारा changed data को consumer की default branch में commit करने से पहले tests चलते हैं; failures होने पर वह branch unchanged रहती है। Updates के बीच consumers offline रहते हुए अपनी bundled copies का उपयोग करते हैं।

किसी consumer में locally update करने के लिए `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` चलाएं। Copies को लिखे बिना stale copies detect करने के लिए `--check` जोड़ें।
