# AGENTS.md

इस repository पर काम करने वाले future agents के लिए guidance।

## Repository Context

यह HackTricks Cloud mdBook repository है। संबंधित main book यहां स्थित है:

`/Users/carlospolop/git/hacktricks`

Shared theme/search behavior में किए गए बदलाव अक्सर दोनों repositories में लागू करने पड़ते हैं।

## Search Index Loading Contract

Custom search UI यहां स्थित है:

`theme/ht_searcher.js`

एक generated copy यहां भी हो सकती है:

`book/theme/ht_searcher.js`

यदि production पहले से बनी हुई `book/` directory deploy कर रहा है, तो दोनों copies update करें या deployment से पहले book rebuild करें।

Search index source policy महत्वपूर्ण और cost-sensitive है:

- Public hosts पर, हर language-specific और fallback candidate को केवल
`HackTricks-wiki/hacktricks-searchindex` से load करें। Same-origin mdBook output पर कभी fallback न करें; production में बड़े index को `cloud.hacktricks.wiki` से serve करना महंगा है।
- Localhost, `.local`/`.internal` hosts, loopback, RFC1918, carrier-grade NAT, link-local या private IPv6 addresses पर, केवल same-origin mdBook output load करें ताकि local/container deployments self-contained रहें। Non-English page के लिए पहले language-prefixed local path आजमाएं (उदाहरण के लिए `/es/searchindex.js`) और root English index को केवल fallback के रूप में उपयोग करें।

इस repo के लिए expected local fallback है:

`/searchindex.js`

इस repo का main-book fallback है:

`/searchindex-book.js`

ये local files केवल private-network sources हैं। Public hosts को exclusively
`HackTricks-wiki/hacktricks-searchindex` में मौजूद remote
`searchindex-<lang>.js.gz` और `searchindex-cloud-<lang>.js.gz` files का उपयोग करना चाहिए।

## Search Index Publishing

Encrypted compressed search indexes को
`HackTricks-wiki/hacktricks-searchindex` पर publish करने वाले workflows हैं:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file `book/searchindex.js` है। Published remote artifact names हैं:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader compact v2 artifact को प्राथमिकता देता है और `.js.gz` artifact को legacy
fallback के रूप में रखता है। दोनों XOR-encrypted gzip payloads हैं, जिनमें
`theme/ht_searcher.js` में परिभाषित key का उपयोग होता है।

Loader lazy रहना चाहिए: सामान्य page navigation को search worker create नहीं करना चाहिए या index download नहीं करना चाहिए, जब तक visitor search open या use न करे। Remote compressed responses को प्रति origin 24 घंटे के लिए Cache Storage में persist किया जाता है ताकि subsequent pages उनका reuse कर सकें। Expired entry को refresh करते समय failure होने पर stale-cache fallback बनाए रखें।

## Build And Validation

सामान्य local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

यदि `mdbook build` fail हो, तो जांचें:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Searching के लिए `rg` को प्राथमिकता दें।
- Generated `book/` output को commits से बाहर रखें, जब तक विशेष रूप से अनुरोध न किया गया हो। Search loader fixes एक exception हैं, जब पहले से बने pages को तुरंत correct करना आवश्यक हो।
- Shared theme behavior बदलते समय, `/Users/carlospolop/git/hacktricks` में matching file की तुलना करें और उसे भी update करें।
- असंबंधित local changes को revert न करें।
