# AGENTS.md

इस repository पर काम करने वाले future agents के लिए guidance।

## Repository Context

यह HackTricks Cloud mdBook repository है। संबंधित main book यहां मौजूद है:

`/Users/carlospolop/git/hacktricks`

Shared theme/search behavior में किए गए changes को अक्सर दोनों repositories में लागू करना आवश्यक होता है।

## Search Index Loading Contract

Custom search UI यहां मौजूद है:

`theme/ht_searcher.js`

एक generated copy यहां भी हो सकती है:

`book/theme/ht_searcher.js`

यदि production पहले से बनी हुई `book/` directory deploy कर रहा है, तो दोनों copies को update करें या deployment से पहले book को rebuild करें।

Search index loading order महत्वपूर्ण और cost-sensitive है:

1. GitHub repository से हर language-specific और fallback search index load करें:
`HackTricks-wiki/hacktricks-searchindex`
2. केवल तभी same-origin mdBook output पर fallback करें, जब GitHub-hosted सभी candidates fail हो जाएं।

`searchindex-cloud-en.js.gz` जैसे किसी भी GitHub-hosted fallback से पहले local `/searchindex.js` fallback न रखें। Production में `cloud.hacktricks.wiki` से `searchindex.js` serve करना महंगा है।

इस repo के लिए expected local fallback है:

`/searchindex.js`

इस repo के लिए main-book fallback है:

`/searchindex-book.js`

यह file केवल fallback है। Primary source को `HackTricks-wiki/hacktricks-searchindex` में मौजूद remote
`searchindex-<lang>.js.gz` और `searchindex-cloud-<lang>.js.gz` files ही रहना चाहिए।

## Search Index Publishing

Encrypted compressed search indexes को `HackTricks-wiki/hacktricks-searchindex` पर publish करने वाले workflows हैं:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Generated source file है `book/searchindex.js`। Published remote artifact names हैं:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader compact v2 artifact को प्राथमिकता देता है और `.js.gz` artifact को legacy fallback के रूप में रखता है। दोनों XOR-encrypted gzip payloads हैं और `theme/ht_searcher.js` में defined key का उपयोग करते हैं।

## Build And Validation

Common local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

यदि `mdbook build` fail हो, तो जांचें:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Searching के लिए `rg` को प्राथमिकता दें।
- Generated `book/` output को commits से बाहर रखें, जब तक स्पष्ट रूप से अनुरोध न किया गया हो। जब पहले से बने pages को तुरंत correct करना हो, तब search loader fixes इसका exception हैं।
- Shared theme behavior बदलते समय `/Users/carlospolop/git/hacktricks` में matching file की तुलना करें और उसे भी update करें।
- Unrelated local changes को revert न करें।
