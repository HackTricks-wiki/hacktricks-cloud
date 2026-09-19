# AGENTS.md

इस repository में काम करने वाले future agents के लिए guidance।

## Repository Context

यह HackTricks Cloud mdBook repository है। संबंधित मुख्य book यहां मौजूद है:

`/Users/carlospolop/git/hacktricks`

Shared theme/search behavior में किए गए changes को अक्सर दोनों repositories में लागू करना आवश्यक होता है।

## Search Index Loading Contract

Custom search UI यहां मौजूद है:

`theme/ht_searcher.js`

एक generated copy यहां भी हो सकती है:

`book/theme/ht_searcher.js`

यदि production पहले से built `book/` directory deploy कर रहा है, तो दोनों copies update करें या deployment से पहले book rebuild करें।

Search index source policy महत्वपूर्ण और cost-sensitive है:

- Public hosts पर, हर language-specific और fallback candidate केवल
`HackTricks-wiki/hacktricks-searchindex` से load करें। Same-origin mdBook output पर कभी fallback न करें; production में `cloud.hacktricks.wiki` से large index serve करना महंगा है।
- Localhost, `.local`/`.internal` hosts, loopback, RFC1918, carrier-grade NAT, link-local या private IPv6 addresses पर केवल same-origin mdBook output load करें, ताकि local/container deployments self-contained रहें।

इस repo के लिए expected local fallback है:

`/searchindex.js`

इस repo के लिए main-book fallback है:

`/searchindex-book.js`

वे local files केवल private-network sources हैं। Public hosts को exclusively
`HackTricks-wiki/hacktricks-searchindex` में मौजूद remote
`searchindex-<lang>.js.gz` और `searchindex-cloud-<lang>.js.gz` files का उपयोग करना चाहिए।

## Search Index Publishing

Encrypted compressed search indexes को
`HackTricks-wiki/hacktricks-searchindex` पर publish करने वाले workflows हैं:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file है `book/searchindex.js`। Published remote artifact names हैं:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader compact v2 artifact को प्राथमिकता देता है और `.js.gz` artifact को legacy fallback के रूप में रखता है। दोनों XOR-encrypted gzip payloads हैं और `theme/ht_searcher.js` में defined key का उपयोग करते हैं।

Loader lazy रहना चाहिए: सामान्य page navigation को search worker create नहीं करना चाहिए और visitor के search खोलने या उपयोग करने तक index download नहीं करना चाहिए। Remote compressed responses को प्रति origin 24 घंटे के लिए Cache Storage में persist किया जाता है, ताकि subsequent pages उनका reuse कर सकें। Expired entry को refresh करते समय failure होने पर stale-cache fallback बनाए रखें।

## Build And Validation

Common local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

यदि `mdbook build` fail हो, तो जांचें:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Searching के लिए `rg` को प्राथमिकता दें।
- Generated `book/` output को commits से बाहर रखें, जब तक विशेष रूप से अनुरोध न किया गया हो। जब पहले से built pages को तुरंत correct करना हो, तब search loader fixes इसका exception हैं।
- Shared theme behavior बदलते समय matching file को
`/Users/carlospolop/git/hacktricks` में compare और update करें।
- Unrelated local changes को revert न करें।
