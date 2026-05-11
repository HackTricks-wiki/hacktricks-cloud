# AGENTS.md

भविष्य के agents के लिए निर्देश, जो इस repository पर काम कर रहे हैं।

## Repository Context

यह HackTricks Cloud mdBook repository है। संबंधित main book यहाँ है:

`/Users/carlospolop/git/hacktricks`

shared theme/search behavior में बदलाव अक्सर दोनों repositories में लागू करने होते हैं।

## Search Index Loading Contract

custom search UI यहाँ है:

`theme/ht_searcher.js`

एक generated copy भी हो सकती है:

`book/theme/ht_searcher.js`

अगर production पहले से built `book/` directory deploy कर रहा है, तो दोनों copies अपडेट करें या deployment से पहले book को rebuild करें।

search index loading order महत्वपूर्ण है और cost-sensitive है:

1. GitHub repository से हर language-specific और fallback search index लोड करें:
`HackTricks-wiki/hacktricks-searchindex`
2. सिर्फ तब, जब सभी GitHub-hosted candidates fail हों, same-origin mdBook output पर fallback करें।

local `/searchindex.js` fallback को किसी भी GitHub-hosted fallback, जैसे
`searchindex-cloud-en.js.gz`, से पहले न रखें। production में `cloud.hacktricks.wiki` से `searchindex.js` serve करना expensive है।

इस repo के लिए expected local fallback है:

`/searchindex.js`

इस repo के लिए main-book fallback है:

`/searchindex-book.js`

वह file सिर्फ fallback है। primary source को remote
`searchindex-<lang>.js.gz` और `searchindex-cloud-<lang>.js.gz` files in
`HackTricks-wiki/hacktricks-searchindex` ही रहना चाहिए।

## Search Index Publishing

encrypted compressed search indexes को `HackTricks-wiki/hacktricks-searchindex` पर publish करने वाले workflows हैं:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

generated source file है `book/searchindex.js`। published remote artifact names हैं:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

browser loader remote `.js.gz` files से XOR-encrypted gzip payloads expect करता है, using the
key defined in `theme/ht_searcher.js`।

## Build And Validation

Common local checks:

- `node --check theme/ht_searcher.js`
- `mdbook build`

अगर `mdbook build` fail होता है, तो check करें:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Editing Notes

- Searching के लिए `rg` को prefer करें।
- generated `book/` output को commits से बाहर रखें, जब तक explicitly requested न हो। Search loader fixes एक exception हैं जब already-built pages को तुरंत correct करना जरूरी हो।
- अगर shared theme behavior बदल रहे हैं, तो matching file को `/Users/carlospolop/git/hacktricks` में compare और update करें।
- unrelated local changes को revert न करें।
