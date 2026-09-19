# AGENTS.md

इस repository में काम करने वाले भविष्य के agents के लिए guidance।

## Repository Context

यह HackTricks Cloud mdBook repository है। संबंधित मुख्य book यहाँ स्थित है:

`/Users/carlospolop/git/hacktricks`

Shared theme/search behavior में किए गए changes अक्सर दोनों repositories में लागू करने पड़ते हैं।

## Search Index Loading Contract

Custom search UI यहाँ स्थित है:

`theme/ht_searcher.js`

एक generated copy यहाँ भी हो सकती है:

`book/theme/ht_searcher.js`

यदि production पहले से बनी हुई `book/` directory deploy कर रहा है, तो दोनों copies update करें या deployment से पहले book rebuild करें।

Search index loading order महत्वपूर्ण और cost-sensitive है:

1. GitHub repository से प्रत्येक language-specific और fallback search index load करें:
`HackTricks-wiki/hacktricks-searchindex`
2. केवल तभी same-origin mdBook output पर fallback करें जब GitHub-hosted सभी candidates fail हो जाएँ।

Local `/searchindex.js` fallback को किसी भी GitHub-hosted fallback, जैसे `searchindex-cloud-en.js.gz`, से पहले न रखें। Production में `cloud.hacktricks.wiki` से `searchindex.js` serve करना महँगा है।

इस repo के लिए expected local fallback है:

`/searchindex.js`

इस repo के लिए main-book fallback है:

`/searchindex-book.js`

यह केवल fallback है। Primary source remote `searchindex-<lang>.js.gz` और `searchindex-cloud-<lang>.js.gz` files ही रहनी चाहिए, जो `HackTricks-wiki/hacktricks-searchindex` में हैं।

## Search Index Publishing

Encrypted compressed search indexes को `HackTricks-wiki/hacktricks-searchindex` पर publish करने वाले workflows हैं:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file `book/searchindex.js` है। Published remote artifact names हैं:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader compact v2 artifact को प्राथमिकता देता है और `.js.gz` artifact को legacy fallback के रूप में रखता है। दोनों XOR-encrypted gzip payloads हैं और `theme/ht_searcher.js` में defined key का उपयोग करते हैं।

Loader lazy रहना चाहिए: सामान्य page navigation को search worker create नहीं करना चाहिए या index download नहीं करना चाहिए, जब तक visitor search को open या use न करे। Remote compressed responses को प्रत्येक origin के लिए 24 घंटे तक Cache Storage में persist किया जाता है, ताकि subsequent pages उनका reuse कर सकें। Expired entry को refresh करते समय failure होने पर stale-cache fallback को बनाए रखें।

## Build And Validation

सामान्य local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

यदि `mdbook build` fail हो, तो जाँच करें:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Searching के लिए `rg` को प्राथमिकता दें।
- Generated `book/` output को commits से बाहर रखें, जब तक विशेष रूप से अनुरोध न किया गया हो। जब पहले से बने हुए pages को तुरंत correct करना हो, तब search loader fixes इसका exception हैं।
- Shared theme behavior बदलते समय `/Users/carlospolop/git/hacktricks` में matching file की तुलना करें और उसे update करें।
- असंबंधित local changes को revert न करें।
