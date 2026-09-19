# AGENTS.md

Рекомендації для майбутніх агентів, які працюють у цьому репозиторії.

## Контекст репозиторію

Це репозиторій HackTricks Cloud mdBook. Пов’язана основна книга розташована за адресою:

`/Users/carlospolop/git/hacktricks`

Зміни до спільної поведінки theme/search часто потрібно застосовувати в обох репозиторіях.

## Контракт завантаження пошукового індексу

Користувацький інтерфейс пошуку розташований у:

`theme/ht_searcher.js`

Також може існувати згенерована копія:

`book/theme/ht_searcher.js`

Якщо production розгортає вже зібраний каталог `book/`, оновіть обидві копії або перебудуйте
книгу перед розгортанням.

Політика джерел пошукового індексу важлива та чутлива до витрат:

- На public hosts завантажуйте кожного кандидата для конкретної мови та fallback лише з
`HackTricks-wiki/hacktricks-searchindex`. Ніколи не використовуйте fallback на mdBook output того самого origin;
  розміщення великого індексу на `cloud.hacktricks.wiki` у production є дорогим.
- На localhost, `.local`/`.internal` hosts, loopback, RFC1918, carrier-grade NAT, link-local або
  private IPv6 addresses завантажуйте лише mdBook output того самого origin, щоб локальні/container deployments
  залишалися self-contained.

Для цього репозиторію очікуваним локальним fallback є:

`/searchindex.js`

Fallback основної книги для цього репозиторію:

`/searchindex-book.js`

Ці локальні файли є джерелами лише для private-network. Public hosts повинні використовувати виключно віддалені
файли `searchindex-<lang>.js.gz` та `searchindex-cloud-<lang>.js.gz` у
`HackTricks-wiki/hacktricks-searchindex`.

## Публікація пошукового індексу

Workflows, які публікують зашифровані стиснені пошукові індекси в
`HackTricks-wiki/hacktricks-searchindex`:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Згенерований source file:

`book/searchindex.js`

Назви опублікованих remote artifacts:

- `searchindex-cloud-v2-en.json.gz` (preferred compact index)
- `searchindex-cloud-v2-<lang>.json.gz` (preferred compact index)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Browser loader надає перевагу compact v2 artifact і зберігає artifact `.js.gz` як legacy
fallback. Обидва є XOR-encrypted gzip payloads із використанням ключа, визначеного в `theme/ht_searcher.js`.

Loader має залишатися lazy: звичайна навігація сторінками не повинна створювати search worker або завантажувати
індекс, доки відвідувач не відкриє або не використає пошук. Remote compressed responses зберігаються в Cache
Storage протягом 24 годин для кожного origin, щоб наступні сторінки могли їх повторно використовувати. Зберігайте
stale-cache fallback, коли оновлення простроченого запису завершується помилкою.

## Збірка та перевірка

Поширені локальні перевірки:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Якщо `mdbook build` завершується помилкою, перевірте:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Примітки щодо редагування

- Для пошуку надавайте перевагу `rg`.
- Не додавайте згенерований output `book/` до commit, якщо це явно не запитано. Виправлення search loader
  є винятком, якщо вже зібрані сторінки потрібно негайно виправити.
- Якщо змінюєте поведінку спільної theme, порівняйте та оновіть відповідний файл у
`/Users/carlospolop/git/hacktricks`.
- Не скасовуйте сторонні локальні зміни.
