# AGENTS.md

Рекомендації для майбутніх агентів, які працюють у цьому repository.

## Контекст repository

Це repository HackTricks Cloud mdBook. Пов’язана основна книга розташована за адресою:

`/Users/carlospolop/git/hacktricks`

Зміни до спільної поведінки theme/search часто потрібно застосовувати в обох repository.

## Контракт завантаження search index

Користувацький search UI розташований у:

`theme/ht_searcher.js`

Також може існувати згенерована копія:

`book/theme/ht_searcher.js`

Якщо production розгортає вже зібраний каталог `book/`, оновіть обидві копії або перебудуйте
книгу перед розгортанням.

Політика джерел search index важлива та чутлива до витрат:

- На public hosts завантажуйте всі language-specific і fallback-кандидати лише з
`HackTricks-wiki/hacktricks-searchindex`. Ніколи не використовуйте same-origin mdBook output як fallback;
роздавання великого index із `cloud.hacktricks.wiki` у production є дорогим.
- На localhost, `.local`/`.internal` hosts, loopback, RFC1918, carrier-grade NAT, link-local або
private IPv6 addresses завантажуйте лише same-origin mdBook output, щоб локальні/container deployments
залишалися self-contained. Для неангломовної сторінки спочатку використовуйте локальний path із префіксом мови
(наприклад `/es/searchindex.js`), а root English index використовуйте лише як fallback.

Для цього repo очікуваним local fallback є:

`/searchindex.js`

Fallback основної книги для цього repo:

`/searchindex-book.js`

Ці локальні файли є джерелами лише для private-network. Public hosts повинні використовувати виключно віддалені
файли `searchindex-<lang>.js.gz` і `searchindex-cloud-<lang>.js.gz` у
`HackTricks-wiki/hacktricks-searchindex`.

## Публікація Search Index

Workflows, які публікують зашифровані стиснені search indexes у
`HackTricks-wiki/hacktricks-searchindex`:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Згенерований source file: `book/searchindex.js`. Назви опублікованих remote artifacts:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader надає перевагу compact v2 artifact і зберігає artifact `.js.gz` як legacy
fallback. Обидва є XOR-encrypted gzip payloads із ключем, визначеним у `theme/ht_searcher.js`.

Loader має залишатися lazy: звичайна навігація сторінками не повинна створювати search worker або завантажувати index,
доки відвідувач не відкриє або не використає search. Віддалені стиснені responses зберігаються в Cache
Storage протягом 24 годин для кожного origin, щоб наступні сторінки могли повторно їх використовувати. Збережіть
stale-cache fallback, якщо оновлення простроченого entry завершується помилкою.

## Збірка та перевірка

Поширені локальні перевірки:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Якщо `mdbook build` завершується помилкою, перевірте:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Нотатки щодо редагування

- Для пошуку надавайте перевагу `rg`.
- Не додавайте згенерований output `book/` до commits, якщо це явно не запитано. Виправлення search loader є
винятком, коли вже зібрані сторінки потрібно негайно виправити.
- Якщо змінюєте поведінку спільної theme, порівняйте та оновіть відповідний файл у
`/Users/carlospolop/git/hacktricks`.
- Не скасовуйте unrelated local changes.
